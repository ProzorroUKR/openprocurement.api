from copy import deepcopy
from itertools import chain

from dateorro import calc_working_datetime

from openprocurement.api.constants import KPKV_UK_SCHEME
from openprocurement.api.constants_env import (
    PLAN_ADDRESS_KIND_REQUIRED_FROM,
    RELEASE_SIMPLE_DEFENSE_FROM,
)
from openprocurement.api.context import get_now, get_request
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.procedure.validation import validate_classifications_prefixes
from openprocurement.api.utils import error_handler, raise_operation_error
from openprocurement.planning.api.constants import (
    BREAKDOWN_OTHER,
    PROCEDURES,
    PROCURING_ENTITY_STANDSTILL,
)
from openprocurement.planning.api.procedure.models.milestone import Milestone
from openprocurement.tender.core.constants import FIRST_STAGE_PROCUREMENT_TYPES
from openprocurement.tender.pricequotation.constants import PQ


class PlanState(BaseState):
    def status_up(self, before, after, data):
        super().status_up(before, after, data)

    def always(self, data):
        super().always(data)

    def on_post(self, data):
        self.validate_on_post(data)
        self._switch_status({}, data)
        self._update_rationale_date(data)
        data["datePublished"] = get_now().isoformat()
        super().on_post(data)

    def on_patch(self, before, after):
        self.validate_on_patch(before, after)
        self._check_field_change_events(before, after)
        self._switch_status(before, after)
        self._update_rationale_date(after, before)
        super().on_patch(before, after)

    def _update_rationale_date(self, after, before=None):
        before = before or {}
        if "rationale" in after:
            if after["rationale"].get("description") != before.get("rationale", {}).get("description"):
                after["rationale"]["date"] = get_now().isoformat()
            else:
                after["rationale"]["date"] = before.get("rationale", {}).get("date", get_now().isoformat())

    def plan_tender_on_post(self, plan, tender):
        self.plan_tender_validate_on_post(plan, tender)

    def tender_plan_on_post(self, plan, tender):
        self.tender_plan_validate_on_post(plan, tender)
        plan["tender_id"] = tender["_id"]
        plan["status"] = "complete"

    def validate_on_post(self, data):
        self._validate_plan_availability(data)
        self._validate_tender_procurement_method_type(data)
        self._validate_items_classification_prefix(data)
        # TODO: turn on later (CS-18891)
        # self.validate_required_additional_classifications(data)

    def validate_on_patch(self, before, after):
        self._validate_plan_changes_in_terminated(before, after)
        self._validate_plan_procurement_method_type_update(before, after)
        self._validate_plan_status_update(before, after)
        self._validate_plan_with_tender(before, after)
        self._validate_items_classification_prefix(after)
        # TODO: turn on later (CS-18891)
        # if before.get("additionalClassifications") != after.get("additionalClassifications"):
        #     self.validate_required_additional_classifications(after)

    def plan_tender_validate_on_post(self, plan, tender):
        self._validate_plan_scheduled(plan)
        self._validate_plan_has_not_tender(plan)
        self._validate_tender_data(tender)
        self._validate_tender_plan_procurement_method_type(tender, plan)
        self._validate_tender_matches_plan(tender, plan)
        self._validate_plan_budget_breakdown(plan)

    def tender_plan_validate_on_post(self, plan, tender):
        self._validate_procurement_kind_is_central(plan, tender)
        self._validate_tender_in_draft(plan, tender)
        self._validate_plan_not_terminated(plan)
        self._validate_plan_has_not_tender(plan)
        self._validate_plan_budget_breakdown(plan)
        self._validate_tender_data(tender)
        self._validate_tender_matches_plan(tender, plan)

    def _check_field_change_events(self, before, after):
        src_identifier = before["procuringEntity"]["identifier"]
        identifier = after["procuringEntity"]["identifier"]
        if src_identifier["scheme"] != identifier["scheme"] or src_identifier["id"] != identifier["id"]:
            if any(m["status"] in Milestone.ACTIVE_STATUSES for m in before.get("milestones", "")):
                standstill_end = calc_working_datetime(get_now(), PROCURING_ENTITY_STANDSTILL)
                if standstill_end.isoformat() > after["tender"]["tenderPeriod"]["startDate"]:
                    raise_operation_error(
                        self.request,
                        "Can't update procuringEntity later than {} "
                        "business days before tenderPeriod.StartDate".format(PROCURING_ENTITY_STANDSTILL.days),
                    )
                # invalidate active milestones and update milestone.dateModified
                for m in after["milestones"]:
                    if m["status"] in Milestone.ACTIVE_STATUSES:
                        m["status"] = Milestone.STATUS_INVALID
                        m["dateModified"] = get_now().isoformat()

    def _switch_status(self, before, after):
        if after.get("cancellation") and after["cancellation"]["status"] == "active":
            self.set_object_status(after, "cancelled", update_date=False)
        elif after.get("tender_id") is not None:
            self.set_object_status(after, "complete", update_date=False)

    def _validate_plan_availability(self, data):
        procurement_method_type = data.get("tender", {}).get("procurementMethodType", "")
        now = get_now()
        if (now >= RELEASE_SIMPLE_DEFENSE_FROM and procurement_method_type == "aboveThresholdUA.defense") or (
            now < RELEASE_SIMPLE_DEFENSE_FROM and procurement_method_type == "simple.defense"
        ):
            raise_operation_error(
                get_request(),
                "procedure with procurementMethodType = {} is not available".format(
                    procurement_method_type,
                ),
            )

    def _validate_tender_procurement_method_type(self, data):
        procedures = deepcopy(PROCEDURES)
        if get_now() >= PLAN_ADDRESS_KIND_REQUIRED_FROM:
            procedures[""] = ("centralizedProcurement",)
        procurement_method_types = list(chain(*procedures.values()))
        procurement_method_types_without_above_threshold_ua_defense = list(
            x for x in procurement_method_types if x not in ("aboveThresholdUA.defense", "simple.defense")
        )
        kind_allows_procurement_method_type_mapping = {
            "defense": procurement_method_types,
            "general": procurement_method_types_without_above_threshold_ua_defense,
            "special": procurement_method_types_without_above_threshold_ua_defense,
            "central": procurement_method_types_without_above_threshold_ua_defense,
            "authority": procurement_method_types_without_above_threshold_ua_defense,
            "social": procurement_method_types_without_above_threshold_ua_defense,
            "other": ["belowThreshold", "reporting", "priceQuotation"],
        }

        kind = data.get("procuringEntity", {}).get("kind", "")
        tender_procurement_method_type = data.get("tender", {}).get("procurementMethodType", "")
        allowed_procurement_method_types = kind_allows_procurement_method_type_mapping.get(kind)
        if allowed_procurement_method_types and get_now() >= PLAN_ADDRESS_KIND_REQUIRED_FROM:
            if tender_procurement_method_type not in allowed_procurement_method_types:
                request = get_request()
                request.errors.add(
                    "body",
                    "kind",
                    "procuringEntity with {kind} kind cannot publish this type of procedure. "
                    "Procurement method types allowed for this kind: {methods}.".format(
                        kind=kind, methods=", ".join(allowed_procurement_method_types)
                    ),
                )
                request.errors.status = 403

    def _validate_plan_not_terminated(self, before):
        status = before.get("status")
        if status in ("cancelled", "complete"):
            request = get_request()
            request.errors.add("body", "status", "Can't update plan in '{}' status".format(status))
            request.errors.status = 422
            raise error_handler(request)

    def _validate_plan_changes_in_terminated(self, before, after):
        status = before.get("status")
        allowed_keys = ("rationale",)
        if status in ("cancelled", "complete"):
            all_keys = set(before.keys()) | set(after.keys())
            keys_to_compare = all_keys - set(allowed_keys)

            for key in keys_to_compare:
                if before.get(key) != after.get(key):
                    raise_operation_error(
                        get_request(),
                        "Can't update {} in {} status".format(key, status),
                    )

    def _validate_plan_procurement_method_type_update(self, before, after):
        new_pmt = after.get("tender", {}).get("procurementMethodType", "")
        current_pmt = before["tender"]["procurementMethodType"]
        now = get_now()

        if current_pmt != new_pmt and (
            now < RELEASE_SIMPLE_DEFENSE_FROM
            and new_pmt == "simple.defense"
            or now > RELEASE_SIMPLE_DEFENSE_FROM
            and new_pmt == "aboveThresholdUA.defense"
        ):
            request = get_request()
            request.errors.add(
                "body",
                "tender",
                "Plan tender.procurementMethodType can not be changed from '{}' to '{}'".format(current_pmt, new_pmt),
            )
            request.errors.status = 422
            raise error_handler(request)

    def _validate_plan_status_update(self, before, after):
        status = before.get("status")
        if after.get("status") == "draft" and status != after.get("status"):
            request = get_request()
            request.errors.add("body", "status", "Plan status can not be changed back to 'draft'")
            request.errors.status = 422
            raise error_handler(request)

    def _validate_plan_with_tender(self, before, after):
        # we need this because of the plans created before the statuses release
        if before.get("tender_id") and not before.get("status"):
            names = []
            if before.get("procuringEntity") != after.get("procuringEntity"):
                names.append("procuringEntity")
            before_breakdown = before.get("budget", {}).get("breakdown")
            after_breakdown = after.get("budget", {}).get("breakdown")
            if before_breakdown != after_breakdown:
                names.append("budget.breakdown")
            request = get_request()
            for name in names:
                request.errors.add(
                    "body",
                    name,
                    "Changing this field is not allowed after tender creation",
                )
            if request.errors:
                request.errors.status = 422
                raise error_handler(request)

    def _validate_plan_scheduled(self, plan):
        status = plan.get("status")
        if status and status != "scheduled":
            request = get_request()
            request.errors.add(
                "body",
                "status",
                "Can't create tender in '{}' plan status".format(status),
            )
            request.errors.status = 422
            raise error_handler(request)

    def _validate_plan_has_not_tender(self, plan):
        if plan.get("tender_id"):
            request = get_request()
            request.errors.add("body", "tender_id", "This plan has already got a tender")
            request.errors.status = 422
            raise error_handler(request)

    def _validate_tender_data(self, tender):
        tender_type = tender.get("procurementMethodType")
        if tender_type not in FIRST_STAGE_PROCUREMENT_TYPES:
            request = get_request()
            request.errors.add(
                "body",
                "procurementMethodType",
                "Should be one of the first stage values: {}".format(
                    FIRST_STAGE_PROCUREMENT_TYPES,
                ),
            )
            request.errors.status = 403
            raise error_handler(request)

    def _validate_tender_plan_procurement_method_type(self, tender, plan):
        tender_type = tender.get("procurementMethodType")
        plan_type = plan["tender"]["procurementMethodType"]
        if plan_type not in (tender_type, "centralizedProcurement"):
            if tender_type == PQ and plan_type == "belowThreshold":
                return
            request = get_request()
            request.errors.add(
                "body",
                "procurementMethodType",
                "procurementMethodType doesn't match: {} != {}".format(plan_type, tender_type),
            )
            request.errors.status = 422
            raise error_handler(request)

    def _validate_tender_matches_plan(self, tender, plan):
        request = get_request()
        plan_identifier = plan["procuringEntity"]["identifier"]
        tender_identifier = tender.get("procuringEntity", {}).get("identifier", {})

        if plan["tender"]["procurementMethodType"] == "centralizedProcurement" and plan_identifier["id"] == "01101100":
            plan_identifier = plan["buyers"][0]["identifier"]

        if plan_identifier["id"] != tender_identifier.get("id") or plan_identifier["scheme"] != tender_identifier.get(
            "scheme"
        ):
            request.errors.add(
                "body",
                "procuringEntity",
                "procuringEntity.identifier doesn't match: {} {} != {} {}".format(
                    plan_identifier["scheme"],
                    plan_identifier["id"],
                    tender_identifier["scheme"],
                    tender_identifier["id"],
                ),
            )

        classification_id = plan["classification"]["id"]
        pattern = classification_id[:3] if classification_id.startswith("336") else classification_id[:4]
        for i, item in enumerate(tender.get("items", "")):
            # item.classification may be empty in pricequotaiton
            if item.get("classification") and item["classification"]["id"][: len(pattern)] != pattern:
                request.errors.add(
                    "body",
                    "items[{}].classification.id".format(i),
                    "Plan classification.id {} and item's {} should be of the same group {}".format(
                        classification_id, item["classification"]["id"], pattern
                    ),
                )

        if request.errors:
            request.errors.status = 422
            raise error_handler(request)

    def _validate_plan_budget_breakdown(self, plan):
        budget = plan.get("budget")
        if not budget or not budget.get("breakdown"):
            request = get_request()
            request.errors.add("body", "budget.breakdown", "Plan should contain budget breakdown")
            request.errors.status = 422
            raise error_handler(request)

    def _validate_procurement_kind_is_central(self, plan, tender):
        kind = "central"
        if tender["procuringEntity"]["kind"] != kind:
            raise raise_operation_error(
                self.request,
                "Only allowed for procurementEntity.kind = '{}'".format(kind),
            )

    def _validate_tender_in_draft(self, plan, tender):
        if tender["status"] != "draft":
            raise raise_operation_error(self.request, "Only allowed in draft tender status")

    def _validate_items_classification_prefix(self, plan):
        classifications = [item["classification"] for item in plan.get("items", [])]
        if not classifications:
            return
        validate_classifications_prefixes(classifications)
        validate_classifications_prefixes(
            classifications,
            root_classification=plan["classification"],
        )

    def validate_required_additional_classifications(self, plan):
        if plan.get("budget") and plan["budget"].get("breakdown"):
            classifications = plan.get("additionalClassifications")
            for breakdown in plan["budget"]["breakdown"]:
                if breakdown.get("title") not in ("own", "loan", BREAKDOWN_OTHER) and (
                    classifications is None
                    or not any(classification["scheme"] == KPKV_UK_SCHEME for classification in classifications)
                ):
                    raise_operation_error(
                        self.request,
                        f"{KPKV_UK_SCHEME} is required for {breakdown['title']} budget.",
                        status=422,
                        name="additionalClassifications",
                    )
