# -*- coding: utf-8 -*-
from openprocurement.api.utils import update_logging_context, error_handler, apply_data_patch, upload_objects_documents
from openprocurement.api.validation import validate_json_data, validate_data
from openprocurement.planning.api.models import Plan, Milestone
from copy import deepcopy


def validate_plan_data(request):
    update_logging_context(request, {"plan_id": "__new__"})
    data = validate_json_data(request)
    if data is None:
        return
    model = request.plan_from_data(data, create=False)
    if hasattr(request, "check_accreditations") and not request.check_accreditations(model.create_accreditations):
        request.errors.add("plan", "accreditation", "Broker Accreditation level does not permit plan creation")
        request.errors.status = 403
        raise error_handler(request.errors)
    data = validate_data(request, model, data=data)
    if data and data.get("mode", None) is None and request.check_accreditations(("t",)):
        request.errors.add("plan", "mode", "Broker Accreditation level does not permit plan creation")
        request.errors.status = 403
        raise error_handler(request.errors)
    return data


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
    upload_objects_documents(request, request.validated["milestone"])
    return milestone


def validate_patch_milestone_data(request):
    model = type(request.context)
    return validate_data(request, model, partial=True)


def validate_milestone_author(request):
    milestone = request.validated["milestone"]
    plan = request.validated["plan"]
    author = milestone.author
    if plan.procuringEntity != author:
        request.errors.add(
            "data",
            "author",
            "Should match plan.procuringEntity"
        )
        request.errors.status = 422
        raise error_handler(request.errors)

    if any(m.author == author for m in plan.milestones if m.status in Milestone.ACTIVE_STATUSES):
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
