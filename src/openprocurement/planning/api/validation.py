# -*- coding: utf-8 -*-
from openprocurement.api.validation import (
    validate_json_data,
    validate_data,
    validate_accreditation_level,
    validate_accreditation_level_mode,
)
from openprocurement.api.utils import update_logging_context, error_handler, upload_objects_documents
from openprocurement.planning.api.models import Plan, Milestone


def validate_plan_data(request):
    update_logging_context(request, {"plan_id": "__new__"})
    data = validate_json_data(request)
    model = request.plan_from_data(data, create=False)
    validate_plan_accreditation_level(request, model)
    data = validate_data(request, model, data=data)
    validate_plan_accreditation_level_mode(request)
    return data


def validate_plan_accreditation_level(request, model):
    levels = model.create_accreditations
    validate_accreditation_level(request, levels, "plan", "plan", "creation")


def validate_plan_accreditation_level_mode(request):
    data = request.validated["data"]
    mode = data.get("mode", None)
    validate_accreditation_level_mode(request, mode, "plan", "plan", "creation")


def validate_patch_plan_data(request):
    return validate_data(request, Plan, True)


def validate_plan_has_not_tender(request):
    plan = request.validated["plan"]
    if plan.tender_id:
        request.errors.add("data", "tender_id", u"This plan has already got a tender")
        request.errors.status = 422
        raise error_handler(request.errors)


def validate_plan_with_tender(request):
    plan = request.validated["plan"]
    if plan.tender_id:
        json_data = request.validated["json_data"]
        names = []
        if "procuringEntity" in json_data:
            names.append("procuringEntity")
        if "budget" in json_data and "breakdown" in json_data["budget"]:
            names.append("budget.breakdown")
        for name in names:
            request.errors.add("data", name, "Changing this field is not allowed after tender creation")
        if request.errors:
            request.errors.status = 422
            raise error_handler(request.errors)


def validate_plan_not_terminated(request):
    plan = request.validated["plan"]
    if plan.status in ("cancelled", "complete"):
        request.errors.add("data", "status", "Can't update plan in '{}' status".format(plan.status))
        request.errors.status = 422
        raise error_handler(request.errors)


def validate_plan_status_update(request):
    status = request.validated["json_data"].get("status")
    if status == "draft" and request.validated["plan"].status != status:
        request.errors.add("data", "status", "Plan status can not be changed back to 'draft'")
        request.errors.status = 422
        raise error_handler(request.errors)


def validate_milestone_data(request):
    update_logging_context(request, {"milestone_id": "__new__"})
    model = type(request.plan).milestones.model_class
    milestone = validate_data(request, model)
    upload_objects_documents(
        request, request.validated["milestone"],
        route_kwargs = {"milestone_id": request.validated["milestone"].id}
    )
    return milestone


def validate_patch_milestone_data(request):
    model = type(request.context)
    return validate_data(request, model, partial=True)


def validate_milestone_author(request):
    milestone = request.validated["milestone"]
    plan = request.validated["plan"]
    author = milestone.author

    plan_identifier = plan.procuringEntity.identifier
    milestone_identifier = author.identifier
    if (plan_identifier.scheme, plan_identifier.id) != (milestone_identifier.scheme, milestone_identifier.id):
        request.errors.add(
            "data",
            "author",
            "Should match plan.procuringEntity"
        )
        request.errors.status = 422
        raise error_handler(request.errors)

    if any(
        (m.author.identifier.scheme, m.author.identifier.id) == (author.identifier.scheme, author.identifier.id)
        for m in plan.milestones
        if m.status in Milestone.ACTIVE_STATUSES
    ):
        request.errors.add(
            "data",
            "author",
            "An active milestone already exists for this author"
        )
        request.errors.status = 422
        raise error_handler(request.errors)


def validate_milestone_status_scheduled(request):
    milestone = request.validated["milestone"]
    if milestone.status != Milestone.STATUS_SCHEDULED:
        request.errors.add(
            "data",
            "status",
            "Cannot create milestone with status: {}".format(milestone["status"])
        )
        request.errors.status = 422
        raise error_handler(request.errors)
