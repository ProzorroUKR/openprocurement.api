from collections import Counter

from openprocurement.api.constants_env import NEW_REQUIREMENTS_RULES_FROM
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import (
    get_tender_category,
    get_tender_profile,
    raise_operation_error,
)
from openprocurement.tender.core.constants import (
    CRITERION_LOCALIZATION,
    CRITERION_TECHNICAL_FEATURES,
)
from openprocurement.tender.core.procedure.models.criterion import ISO_MAPPING
from openprocurement.tender.core.procedure.utils import tender_created_after


class TenderCriterionMixin:
    def _validate_criterion_uniq(self, data, previous_criteria=[]) -> None:
        new_criteria = {}

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

        def validate_string(req):
            if req.get("expectedValues") is None:
                raise_requirement_error("expectedValues is required when dataType is string")
            if len(req["expectedValues"]) != len(set(req["expectedValues"])):
                raise_requirement_error("expectedValues should be unique")
            if req.get("expectedMinItems") != 1:
                raise_requirement_error("expectedMinItems is required and should be equal to 1 for dataType string")
            if req.get("unit"):
                raise_requirement_error("unit is forbidden for dataType string")
            if req.get("dataSchema") is not None and set(req["expectedValues"]) - set(ISO_MAPPING[req["dataSchema"]]):
                raise_requirement_error(
                    f"expectedValues should have {req['dataSchema']} format and include codes from standards"
                )

        def validate_boolean(req):
            if req.get("expectedValues") is not None:  # minValue/maxValue check exists in Requirement model
                raise_requirement_error("only expectedValue is allowed for dataType boolean")
            if req.get("unit"):
                raise_requirement_error("unit is forbidden for dataType boolean")
            if req.get("dataSchema") is not None:
                raise_requirement_error("dataSchema is allowed only for dataType string")

        def validate_number_or_integer(req):
            for str_field in ("expectedValues", "dataSchema"):
                if req.get(str_field) is not None:
                    raise_requirement_error(f"{str_field} is allowed only for dataType string")
            if req.get("expectedValue") is None and req.get("minValue") is None:
                raise_requirement_error(f"expectedValue or minValue is required for dataType {req['dataType']}")
            if not req.get("unit"):
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
                        validation_rules[data_type](req)

    def validate_criteria_requirement_from_market(self, data: dict) -> None:
        if not tender_created_after(NEW_REQUIREMENTS_RULES_FROM):
            return
        tender = get_tender()
        if not isinstance(data, list):
            data = [data]

        # get profile and category for each tender item
        tender_items_market_objects = {
            item["id"]: (item.get("profile"), item.get("category")) for item in tender.get("items", [])
        }

        for tender_criterion in data:
            # check only localization and tech criteria, because only these are in market
            if tender_criterion["classification"]["id"] in (CRITERION_TECHNICAL_FEATURES, CRITERION_LOCALIZATION):
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

                for market_criterion in market_obj.get("criteria", []):
                    if market_criterion.get("classification", {}).get("id") == tender_criterion["classification"]["id"]:
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
                        }
                        if set(tender_requirements.keys()) - set(market_requirements.keys()):
                            raise_operation_error(
                                self.request,
                                f"For criterion {tender_criterion['classification']['id']} there are "
                                f"requirements that don't exist in {'profile' if requirements_from_profile else 'category'} "
                                f"or archived: {set(tender_requirements.keys()) - set(market_requirements.keys())}",
                                status=422,
                            )
                        if requirements_from_profile and set(market_requirements.keys()) - set(
                            tender_requirements.keys()
                        ):
                            raise_operation_error(
                                self.request,
                                f"Criterion {tender_criterion['classification']['id']} lacks requirements from "
                                f"profile {set(market_requirements.keys()) - set(tender_requirements.keys())}",
                                status=422,
                            )
                        for market_req in list(market_requirements.values()):
                            if tender_req := tender_requirements.get(market_req["title"]):
                                fields = ["title", "unit", "dataType", "expectedMaxItems", "dataSchema"]
                                if requirements_from_profile:
                                    fields.extend(
                                        ["expectedValue", "expectedMinItems", "expectedValues", "minValue", "maxValue"]
                                    )
                                for field in fields:
                                    if field == "expectedValues" and market_req.get(field):
                                        # Counter works like set but check the length of lists too
                                        if Counter(tender_req.get(field)) != Counter(market_req[field]):
                                            raise_operation_error(
                                                self.request,
                                                f"Field '{field}' for '{market_req['title']}' should have the same values in tender and market requirement",
                                                status=422,
                                            )
                                    elif market_req.get(field) != tender_req.get(field):
                                        raise_operation_error(
                                            self.request,
                                            f"Field '{field}' for '{market_req['title']}' should be equal in tender and market requirement",
                                            status=422,
                                        )
                                if not requirements_from_profile and (
                                    expected_values := market_req.get("expectedValues")
                                ):
                                    if not tender_req.get("expectedValues") or set(
                                        tender_req["expectedValues"]
                                    ).difference(set(expected_values)):
                                        raise_operation_error(
                                            self.request,
                                            f"Requirement '{tender_req['title']}' expectedValues should have values "
                                            f"from category requirement",
                                            status=422,
                                        )
