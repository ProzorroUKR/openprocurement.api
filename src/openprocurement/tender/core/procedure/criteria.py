from collections import Counter
from typing import Any, Optional, Tuple, Union

from pyramid.request import Request

from openprocurement.api.constants import CRITERIA_LIST
from openprocurement.api.constants_env import (
    CRITERIA_CLASSIFICATION_VALIDATION_FROM,
    NEW_REQUIREMENTS_RULES_FROM,
    UNIFIED_CRITERIA_LOGIC_FROM,
)
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.api.utils import (
    get_tender_category,
    get_tender_profile,
    raise_operation_error,
)
from openprocurement.tender.core.constants import (
    CRITERION_LOCALIZATION,
    CRITERION_TECHNICAL_FEATURES,
)
from openprocurement.tender.core.procedure.models.criterion import (
    ISO_MAPPING,
    ReqStatuses,
)
from openprocurement.tender.core.procedure.utils import tender_created_after


class TenderCriterionMixin:
    request: Request
    should_validate_required_market_criteria: bool

    def _validate_criterion_uniq(self, data, previous_criteria=[]) -> None:
        new_criteria: dict[str, Any] = {}

        def check(new_criterion: dict) -> None:
            if class_id := new_criterion.get("classification", {}).get("id"):
                if class_id in new_criteria:
                    if new_criterion.get("relatesTo") in ("lot", "item"):
                        if new_criterion["relatedItem"] in new_criteria[class_id].get("lots", []):
                            raise_operation_error(self.request, "Criteria are not unique")
                        elif not new_criteria[class_id].get("lots", []):
                            new_criteria[class_id]["lots"] = [new_criterion["relatedItem"]]
                        else:
                            new_criteria[class_id]["lots"].append(new_criterion["relatedItem"])
                    elif not new_criteria[class_id].get("tenderer", False):
                        new_criteria[class_id] = {"tenderer": True}
                    else:
                        raise_operation_error(self.request, "Criteria are not unique")
                elif new_criterion.get("relatesTo") in ("lot", "item"):
                    new_criteria[class_id] = {"lots": [new_criterion["relatedItem"]]}
                else:
                    new_criteria[class_id] = {"tenderer": True}

                for existed_criterion in previous_criteria:
                    if (
                        new_criterion.get("relatesTo") == existed_criterion.get("relatesTo")
                        and new_criterion.get("relatedItem") == existed_criterion.get("relatedItem")
                        and new_criterion["classification"]["id"] == existed_criterion["classification"]["id"]
                    ):
                        raise_operation_error(self.request, "Criteria are not unique")

        if isinstance(data, list):
            for new_criterion in data:
                check(new_criterion)
        else:
            check(data)

    def validate_criteria_requirements_rules(self, data: dict) -> None:
        if not tender_created_after(NEW_REQUIREMENTS_RULES_FROM):
            return
        if not isinstance(data, list):
            data = [data]

        def raise_requirement_error(message):
            raise_operation_error(
                self.request,
                message,
                status=422,
                name="requirements",
            )

        def validate_string(req, criteria_id):
            if req.get("expectedValues") is None:
                raise_requirement_error("expectedValues is required when dataType is string")
            if len(req["expectedValues"]) != len(set(req["expectedValues"])):
                raise_requirement_error("expectedValues should be unique")
            if req.get("expectedMinItems") is None:
                raise_requirement_error("expectedMinItems is required for dataType string")
            if criteria_id != CRITERION_TECHNICAL_FEATURES and req.get("expectedMinItems") != 1:
                raise_requirement_error("expectedMinItems should be equal to 1 for dataType string")
            if req.get("unit"):
                raise_requirement_error("unit is forbidden for dataType string")
            if req.get("dataSchema") is not None and set(req["expectedValues"]) - set(ISO_MAPPING[req["dataSchema"]]):
                raise_requirement_error(
                    f"expectedValues should have {req['dataSchema']} format and include codes from standards"
                )

        def validate_boolean(req, criteria_id):
            if req.get("expectedValues") is not None:  # minValue/maxValue check exists in Requirement model
                raise_requirement_error("only expectedValue is allowed for dataType boolean")
            if req.get("unit"):
                raise_requirement_error("unit is forbidden for dataType boolean")
            if req.get("dataSchema") is not None:
                raise_requirement_error("dataSchema is allowed only for dataType string")

        def validate_number_or_integer(req, criteria_id):
            for str_field in ("expectedValues", "dataSchema"):
                if req.get(str_field) is not None:
                    raise_requirement_error(f"{str_field} is allowed only for dataType string")
            if req.get("expectedValue") is None and req.get("minValue") is None:
                raise_requirement_error(f"expectedValue or minValue is required for dataType {req['dataType']}")
            if req.get("minValue") is not None and req.get("maxValue") is not None:
                if req["maxValue"] < req["minValue"]:
                    raise_requirement_error("maxValue should be greater than minValue")
            # for technical features unit should be from profile/category (may exist/ may be empty)
            if criteria_id != CRITERION_TECHNICAL_FEATURES and not req.get("unit"):
                raise_requirement_error(f"unit is required for dataType {req['dataType']}")

        validation_rules = {
            "string": validate_string,
            "boolean": validate_boolean,
            "number": validate_number_or_integer,
            "integer": validate_number_or_integer,
        }

        for tender_criterion in data:
            for rg in tender_criterion.get("requirementGroups", []):
                for req in rg.get("requirements", []):
                    data_type = req.get("dataType")
                    if data_type in validation_rules:
                        validation_rules[data_type](req, tender_criterion.get("classification", {}).get("id"))

    def _resolve_market_criterion(self, tender_criterion: dict) -> Optional[Tuple[dict, str, bool]]:
        # check only localization and tech criteria, because only these are in market
        market_criteria_ids = (CRITERION_TECHNICAL_FEATURES, CRITERION_LOCALIZATION)
        if tender_criterion["classification"]["id"] not in market_criteria_ids:
            return None

        tender = get_tender()
        tender_items_market_objects = {
            item["id"]: (item.get("profile"), item.get("category")) for item in tender.get("items", [])
        }

        # find market object: profile or category
        market_obj: dict = {}
        requirements_from_profile = False
        profile_id, category_id = tender_items_market_objects[tender_criterion["relatedItem"]]
        if profile_id:
            profile = get_tender_profile(self.request, profile_id)
            if profile.get("status", "active") == "active":
                requirements_from_profile = True
                market_obj = profile

        # check requirements from category only if there is no profile in item or profile is general
        if not requirements_from_profile and category_id:
            market_obj = get_tender_category(self.request, category_id)

        if not market_obj:
            return None

        market_id = market_obj["id"]

        # Search for matching market criterion
        for market_criterion in market_obj.get("criteria", []):
            if market_criterion.get("classification", {}).get("id") == tender_criterion["classification"]["id"]:
                return market_criterion, market_id, requirements_from_profile

        return None

    def validate_criteria_requirement_from_market(self, data: Union[dict, list]) -> None:
        if not tender_created_after(NEW_REQUIREMENTS_RULES_FROM):
            return

        if not isinstance(data, list):
            data = [data]

        for tender_criterion in data:
            resolved = self._resolve_market_criterion(tender_criterion)
            if resolved is None:
                continue
            market_criterion, market_id, requirements_from_profile = resolved

            # Validate tender criterion requirements against market criterion
            self._validate_market_criterion_requirements(
                tender_criterion=tender_criterion,
                market_criterion=market_criterion,
                market_id=market_id,
                requirements_from_profile=requirements_from_profile,
            )

    def validate_requirement_from_market(self, tender_criterion: dict, requirement: dict) -> None:
        if not tender_created_after(NEW_REQUIREMENTS_RULES_FROM):
            return

        # cancelled / non-active requirements are validated against the market at activation
        if requirement.get("status", ReqStatuses.DEFAULT) != ReqStatuses.ACTIVE:
            return

        resolved = self._resolve_market_criterion(tender_criterion)
        if resolved is None:
            return
        market_criterion, market_id, requirements_from_profile = resolved

        market_requirements = {
            req["title"]: req
            for rg in market_criterion.get("requirementGroups", "")
            for req in rg.get("requirements", "")
            if not req.get("isArchived", False)
        }
        market_req = market_requirements.get(requirement["title"])

        # a requirement whose title is absent from the market is a composition concern (activation)
        if not market_req:
            return

        self._validate_market_requirement_fields(
            tender_req=requirement,
            market_req=market_req,
            market_id=market_id,
            requirements_from_profile=requirements_from_profile,
        )

    def _validate_market_criterion_requirements(
        self,
        tender_criterion: dict,
        market_criterion: dict,
        market_id: str,
        requirements_from_profile: bool,
    ) -> None:
        market_ref = "profile" if requirements_from_profile else "category"
        market_requirements = {
            req["title"]: req
            for rg in market_criterion.get("requirementGroups", "")
            for req in rg.get("requirements", "")
            if not req.get("isArchived", False)
        }
        tender_requirements = {
            req["title"]: req
            for rg in tender_criterion.get("requirementGroups", "")
            for req in rg.get("requirements", "")
            if req.get("status", ReqStatuses.DEFAULT) == ReqStatuses.ACTIVE
        }
        market_requirements_ids = set(market_requirements.keys())
        tender_requirements_ids = set(tender_requirements.keys())

        # Validate that tender requirements exist in market
        if tender_requirements_ids - market_requirements_ids:
            raise_operation_error(
                self.request,
                f"For criterion {tender_criterion['classification']['id']} there are "
                f"requirements that don't exist in {market_ref} "
                f"{market_id} or archived: {tender_requirements_ids - market_requirements_ids}",
                status=422,
            )

        # Check if validation enabled
        if tender_created_after(UNIFIED_CRITERIA_LOGIC_FROM) and not self.should_validate_required_market_criteria:
            pass

        elif requirements_from_profile or tender_criterion["classification"]["id"] == CRITERION_LOCALIZATION:
            if market_requirements_ids - tender_requirements_ids:
                raise_operation_error(
                    self.request,
                    f"Criterion {tender_criterion['classification']['id']} lacks requirements from "
                    f"{market_ref} {market_id} {market_requirements_ids - tender_requirements_ids}",
                    status=422,
                )
        elif not tender_requirements_ids.intersection(market_requirements_ids):
            raise_operation_error(
                self.request,
                f"Criterion {tender_criterion['classification']['id']} should have at least "
                f"one requirement from category {market_id}",
                status=422,
            )

        # Validate each market requirement against tender requirement
        for market_req in list(market_requirements.values()):
            tender_req = tender_requirements.get(market_req["title"])

            if not tender_req:
                continue

            self._validate_market_requirement_fields(
                tender_req=tender_req,
                market_req=market_req,
                market_id=market_id,
                requirements_from_profile=requirements_from_profile,
            )

    def _validate_market_requirement_fields(
        self,
        tender_req: dict,
        market_req: dict,
        market_id: str,
        requirements_from_profile: bool,
    ) -> None:
        base_fields = [
            "title",
            "unit",
            "dataType",
            "dataSchema",
            "expectedMinItems",
            "expectedMaxItems",
            "expectedValues",
        ]
        profile_only_fields = [
            "expectedValue",
            "minValue",
            "maxValue",
        ]
        fields = base_fields + (profile_only_fields if requirements_from_profile else [])

        for field in fields:
            self._validate_market_requirement_field(
                field=field,
                tender_req=tender_req,
                market_req=market_req,
                market_id=market_id,
                requirements_from_profile=requirements_from_profile,
            )

    def _validate_market_requirement_field(
        self,
        field: str,
        tender_req: dict,
        market_req: dict,
        market_id: str,
        requirements_from_profile: bool,
    ) -> None:
        market_ref = "profile" if requirements_from_profile else "category"

        same_ref_error = (
            f"Field '{{field}}' for '{market_req['title']}' should have the same values in "
            f"tender and market requirement for {market_ref} {market_id}"
        )
        equal_ref_error = (
            f"Field '{{field}}' for '{market_req['title']}' should be equal in tender and market "
            f"requirement for {market_ref} {market_id}"
        )

        # Validate expectedValues for profile
        if field == "expectedValues" and requirements_from_profile:
            market_expected_values = market_req.get("expectedValues") or []
            tender_expected_values = tender_req.get("expectedValues") or []
            # Counter is multiset-aware; also treats list length.
            if Counter(tender_expected_values) != Counter(market_expected_values):
                raise_operation_error(
                    self.request,
                    same_ref_error.format(field=field),
                    status=422,
                )
            return

        # Validate expectedValues for category
        if field == "expectedValues" and not requirements_from_profile:
            market_expected_values = market_req.get("expectedValues") or []
            tender_expected_values = tender_req.get("expectedValues") or []
            if set(tender_expected_values).difference(set(market_expected_values)):
                raise_operation_error(
                    self.request,
                    f"Requirement '{tender_req['title']}' expectedValues should have values "
                    f"from category {market_id} requirement",
                    status=422,
                )
            return

        # Validate expectedMinItems / expectedMaxItems narrowing
        if field == "expectedMinItems" and not requirements_from_profile:
            market_min = market_req.get("expectedMinItems")
            tender_min = tender_req.get("expectedMinItems")

            if market_min is not None and (tender_min is None or tender_min < market_min):
                raise_operation_error(
                    self.request,
                    f"requirement '{market_req['title']}' expectedMinItems should be equal or greater than in category",
                    status=422,
                )

            return

        if field == "expectedMaxItems" and not requirements_from_profile:
            tender_max = tender_req.get("expectedMaxItems")
            market_max = market_req.get("expectedMaxItems")

            if market_max is not None and (tender_max is None or tender_max > market_max):
                raise_operation_error(
                    self.request,
                    f"requirement '{market_req['title']}' expectedMaxItems should be equal or less than in category",
                    status=422,
                )

            return

        # Convert number fields
        market_field = market_req.get(field)
        if (
            market_req.get("dataType") == "number"
            and field in ("expectedValue", "minValue", "maxValue")
            and market_field is not None
        ):
            # Market and CBD may store numbers as different types (e.g. float vs decimal).
            market_field = to_decimal(market_field)

        # Default validation - exact match
        if market_field != tender_req.get(field):
            raise_operation_error(
                self.request,
                equal_ref_error.format(field=field),
                status=422,
            )

    def validate_criteria_classification(self, data: Union[dict, list]) -> None:
        if not tender_created_after(CRITERIA_CLASSIFICATION_VALIDATION_FROM):
            return

        if not isinstance(data, list):
            data = [data]

        for tender_criterion in data:
            if tender_criterion["classification"]["id"] not in CRITERIA_LIST:
                raise_operation_error(
                    self.request,
                    f"Criteria classification {tender_criterion['classification']['id']} not from standards",
                    status=422,
                    name="criteria",
                )
