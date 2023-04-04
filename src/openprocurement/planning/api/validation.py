# -*- coding: utf-8 -*-
from openprocurement.api.validation import (
    validate_json_data,
    validate_data,
    _validate_accreditation_level,
    _validate_accreditation_level_mode,
)
from openprocurement.api.constants import RELEASE_SIMPLE_DEFENSE_FROM
from openprocurement.api.utils import (
    update_logging_context,
    error_handler,
    upload_objects_documents,
    raise_operation_error,
)
from openprocurement.planning.api.models import Plan, Milestone
from openprocurement.planning.api.constants import PROCEDURES
from openprocurement.tender.core.constants import FIRST_STAGE_PROCUREMENT_TYPES
from itertools import chain
from openprocurement.api.utils import get_now
from openprocurement.api.constants import PLAN_ADDRESS_KIND_REQUIRED_FROM
from copy import deepcopy


def validate_plan_data(request, **kwargs):
    update_logging_context(request, {"plan_id": "__new__"})
    data = validate_json_data(request)
    model = request.plan_from_data(data, create=False)
    _validate_plan_accreditation_level(request, model)
    data = validate_data(request, model, data=data)
    _validate_plan_availability(request)
    _validate_plan_accreditation_level_mode(request)
    _validate_tender_procurement_method_type(request)
    return data


def _validate_plan_accreditation_level(request, model):
    _validate_accreditation_level(request, model.create_accreditations, "plan", "creation")


def _validate_plan_accreditation_level_mode(request):
    data = request.validated["data"]
    mode = data.get("mode", None)
    _validate_accreditation_level_mode(request, mode, "plan", "creation")


def _validate_plan_availability(request):
    data = request.validated["data"]
    procurement_method_type = data.get("tender", {}).get("procurementMethodType", "")
    now = get_now()
    if (
        (now >= RELEASE_SIMPLE_DEFENSE_FROM and procurement_method_type == "aboveThresholdUA.defense")
        or (now < RELEASE_SIMPLE_DEFENSE_FROM and procurement_method_type == "simple.defense")
    ):
        raise_operation_error(
            request,
            "procedure with procurementMethodType = {} is not available".format(procurement_method_type),
        )


def _validate_tender_procurement_method_type(request):
    _procedures = deepcopy(PROCEDURES)
    if get_now() >= PLAN_ADDRESS_KIND_REQUIRED_FROM:
        _procedures[""] = ("centralizedProcurement", )
    procurement_method_types = list(chain(*_procedures.values()))
    procurement_method_types_without_above_threshold_ua_defense = list(
        [x for x in procurement_method_types if x not in ('aboveThresholdUA.defense', 'simple.defense')]
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

    data = request.validated["data"]
    kind = data.get("procuringEntity", {}).get("kind", "")
    tender_procurement_method_type = data.get("tender", {}).get("procurementMethodType", "")
    allowed_procurement_method_types = kind_allows_procurement_method_type_mapping.get(kind)
    if allowed_procurement_method_types and get_now() >= PLAN_ADDRESS_KIND_REQUIRED_FROM:
        if tender_procurement_method_type not in allowed_procurement_method_types:
            request.errors.add(
                "body", "kind",
                "procuringEntity with {kind} kind cannot publish this type of procedure. "
                "Procurement method types allowed for this kind: {methods}.".format(
                    kind=kind, methods=", ".join(allowed_procurement_method_types)
                )
            )
            request.errors.status = 403


def validate_patch_plan_data(request, **kwargs):
    return validate_data(request, Plan, True)


def validate_plan_has_not_tender(request, **kwargs):
    plan = request.validated["plan"]
    if plan.tender_id:
        request.errors.add("body", "tender_id", "This plan has already got a tender")
        request.errors.status = 422
        raise error_handler(request)


def validate_plan_with_tender(request, **kwargs):
    plan = request.validated["plan"]
    if plan.tender_id:
        json_data = request.validated["json_data"]
        names = []
        if "procuringEntity" in json_data:
            names.append("procuringEntity")
        if "budget" in json_data and "breakdown" in json_data["budget"]:
            names.append("budget.breakdown")
        for name in names:
            request.errors.add("body", name, "Changing this field is not allowed after tender creation")
        if request.errors:
            request.errors.status = 422
            raise error_handler(request)


def validate_plan_not_terminated(request, **kwargs):
    plan = request.validated["plan"]
    if plan.status in ("cancelled", "complete"):
        request.errors.add("body", "status", "Can't update plan in '{}' status".format(plan.status))
        request.errors.status = 422
        raise error_handler(request)


def validate_plan_scheduled(request, **kwargs):
    plan = request.validated["plan"]
    if plan.status != "scheduled":
        request.errors.add("body", "status", "Can't create tender in '{}' plan status".format(plan.status))
        request.errors.status = 422
        raise error_handler(request)


def validate_plan_status_update(request, **kwargs):
    status = request.validated["json_data"].get("status")
    if status == "draft" and request.validated["plan"].status != status:
        request.errors.add("body", "status", "Plan status can not be changed back to 'draft'")
        request.errors.status = 422
        raise error_handler(request)


def validate_plan_procurementMethodType_update(request, **kwargs):
    new_pmt = request.validated["json_data"].get("tender", {}).get("procurementMethodType", "")
    current_pmt = request.validated["plan"].tender.procurementMethodType

    now = get_now()

    if (
        current_pmt != new_pmt
        and (
            now < RELEASE_SIMPLE_DEFENSE_FROM and new_pmt == "simple.defense"
            or now > RELEASE_SIMPLE_DEFENSE_FROM and new_pmt == "aboveThresholdUA.defense"
        )
    ):
        request.errors.add(
            "body",
            "tender",
            "Plan tender.procurementMethodType can not be changed from '{}' to '{}'".format(
                current_pmt, new_pmt
            )
        )
        request.errors.status = 422
        raise error_handler(request)


def validate_milestone_data(request, **kwargs):
    update_logging_context(request, {"milestone_id": "__new__"})
    model = type(request.plan).milestones.model_class
    milestone = validate_data(request, model)
    upload_objects_documents(
        request, request.validated["milestone"],
        route_kwargs={"milestone_id": request.validated["milestone"].id}
    )
    return milestone


def validate_patch_milestone_data(request, **kwargs):
    model = type(request.context)
    return validate_data(request, model, partial=True)


def validate_milestone_author(request, **kwargs):
    milestone = request.validated["milestone"]
    plan = request.validated["plan"]
    author = milestone.author

    plan_identifier = plan.procuringEntity.identifier
    milestone_identifier = author.identifier
    if (plan_identifier.scheme, plan_identifier.id) != (milestone_identifier.scheme, milestone_identifier.id):
        request.errors.add(
            "body",
            "author",
            "Should match plan.procuringEntity"
        )
        request.errors.status = 422
        raise error_handler(request)

    if any(
        (m.author.identifier.scheme, m.author.identifier.id) == (author.identifier.scheme, author.identifier.id)
        for m in plan.milestones
        if m.status in Milestone.ACTIVE_STATUSES
    ):
        request.errors.add(
            "body",
            "author",
            "An active milestone already exists for this author"
        )
        request.errors.status = 422
        raise error_handler(request)


def validate_milestone_status_scheduled(request, **kwargs):
    milestone = request.validated["milestone"]
    if milestone.status != Milestone.STATUS_SCHEDULED:
        request.errors.add(
            "body",
            "status",
            "Cannot create milestone with status: {}".format(milestone["status"])
        )
        request.errors.status = 422
        raise error_handler(request)


def validate_tender_data(request, **kwargs):
    data = validate_json_data(request)
    if data.get("procurementMethodType") not in FIRST_STAGE_PROCUREMENT_TYPES:
        request.errors.add(
            "body",
            "procurementMethodType",
            "Should be one of the first stage values: {}".format(FIRST_STAGE_PROCUREMENT_TYPES),
        )
        request.errors.status = 403
        raise error_handler(request)

    request.validated["tender_data"] = data

    config = request.json.get("config", {})
    request.validated["tender_config"] = config
