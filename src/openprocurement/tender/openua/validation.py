from datetime import timedelta

from schematics.exceptions import ValidationError

from openprocurement.api.constants import RELEASE_2020_04_19, WORKING_DAYS
from openprocurement.api.validation import (
    validate_data,
    OPERATIONS,
    _validate_accreditation_level,
    _validate_accreditation_level_mode,
    validate_tender_first_revision_date,
)
from openprocurement.api.utils import (
    error_handler, get_now, raise_operation_error,
    update_logging_context,
    upload_objects_documents,
)
from openprocurement.tender.core.utils import calculate_tender_business_date, calculate_tender_date
from openprocurement.tender.openua.constants import POST_SUBMIT_TIME


def _validate_tender_period_start_date(data, period, working_days=False, calendar=WORKING_DAYS):
    min_allowed_date = calculate_tender_date(
        get_now(),
        - timedelta(minutes=10),
        tender=None,
        working_days=working_days,
        calendar=calendar
    )
    if min_allowed_date >= period.startDate:
        raise ValidationError("tenderPeriod.startDate should be in greater than current date")


# complaint
def validate_submit_claim_time(request, **kwargs):
    tender = request.validated["tender"]
    claim_submit_time = request.content_configurator.tender_claim_submit_time
    claim_end_date = calculate_tender_business_date(tender.tenderPeriod.endDate, -claim_submit_time, tender)
    if get_now() > claim_end_date:
        raise_operation_error(
            request,
            "Can submit claim not later than {duration.days} "
            "full calendar days before tenderPeriod ends".format(
                duration=claim_submit_time
            )
        )


# complaint documents
def validate_complaint_document_operation_not_in_allowed_status(request, **kwargs):
    if request.validated["tender_status"] not in ["active.tendering"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


# contract
def validate_contract_update_with_accepted_complaint(request, **kwargs):
    tender = request.validated["tender"]
    if any(
        [
            any([c.status == "accepted" for c in i.complaints])
            for i in tender.awards
            if i.lotID in [a.lotID for a in tender.awards if a.id == request.context.awardID]
        ]
    ):
        raise_operation_error(request, "Can't update contract with accepted complaint")


def validate_accepted_complaints(request, **kwargs):
    if any(
        [
            any([c.status == "accepted" for c in i.complaints])
            for i in request.validated["tender"].awards
            if i.lotID == request.validated["award"].lotID
        ]
    ):
        operation = OPERATIONS.get(request.method)
        raise_operation_error(request, "Can't {} document with accepted complaint".format(operation))


# cancellation
def validate_not_only_unsuccessful_awards_or_qualifications(request, **kwargs):
    unsuccessful_statuses = {"unsuccessful", "cancelled"}
    tender = request.validated["tender"]
    cancellation = request.validated["cancellation"]
    # we use below getattr, so we can use validator bot for openua and openeu procedures
    items = tender.awards if tender.awards else getattr(tender, "qualifications", "")

    def raise_error():
        raise_operation_error(
            request,
            "Can't perform cancellation if all {} are unsuccessful".format(
                "awards" if tender.awards else "qualifications"
            ),
        )

    if not cancellation.relatedLot and tender.lots:
        # cancelling tender with lots
        # can't cancel tender if there is a lot, where
        active_lots = (i.id for i in tender.lots if i.status == "active")
        for lot_id in active_lots:
            item_statuses = {i.status for i in items if i.lotID == lot_id}
            if item_statuses and not item_statuses.difference(unsuccessful_statuses):
                raise_error()

    elif cancellation.relatedLot and tender.lots or not cancellation.relatedLot and not tender.lots:
        # cancelling lot or tender without lots
        statuses = {i.status for i in items if i.lotID == cancellation.relatedLot}
        if statuses and not statuses.difference(unsuccessful_statuses):
            raise_error()


# post
def _validate_post_accreditation_level(request, **kwargs):
    tender = request.validated["tender"]
    mode = tender.get("mode", None)
    _validate_accreditation_level(request, tender.edit_accreditations, "post", "creation")
    _validate_accreditation_level_mode(request, mode, "post", "creation")


def validate_complaint_post_data(request, **kwargs):
    update_logging_context(request, {"post_id": "__new__"})
    _validate_post_accreditation_level(request)
    model = type(request.context).posts.model_class
    post = validate_data(request, model)
    upload_objects_documents(
        request, request.validated["post"],
        route_kwargs={"post_id": request.validated["post"].id}
    )
    return post


def validate_award_complaint_post_data(request, **kwargs):
    update_logging_context(request, {"post_id": "__new__"})
    _validate_post_accreditation_level(request)
    model = type(request.context).posts.model_class
    post = validate_data(request, model)
    upload_objects_documents(
        request, request.validated["post"],
        route_kwargs={"post_id": request.validated["post"].id}
    )
    return post


def validate_cancellation_complaint_post_data(request, **kwargs):
    update_logging_context(request, {"post_id": "__new__"})
    _validate_post_accreditation_level(request)
    model = type(request.tender).cancellations.model_class.complaints.model_class.posts.model_class
    post = validate_data(request, model)
    upload_objects_documents(
        request, request.validated["post"],
        route_kwargs={"post_id": request.validated["post"].id}
    )
    return post


def validate_qualification_complaint_post_data(request, **kwargs):
    update_logging_context(request, {"post_id": "__new__"})
    _validate_post_accreditation_level(request)
    model = type(request.context).posts.model_class
    post = validate_data(request, model)
    upload_objects_documents(
        request, request.validated["post"],
        route_kwargs={"post_id": request.validated["post"].id}
    )
    return post


def validate_complaint_post_complaint_type(request, **kwargs):
    complaint = request.validated["complaint"]
    if complaint.type != "complaint":
        raise_operation_error(
            request, "Can't submit or edit post in current ({}) complaint type".format(
                complaint.type
            )
        )


def validate_complaint_post_complaint_status(request, **kwargs):
    complaint = request.validated["complaint"]
    if complaint.status not in ["pending", "accepted"]:
        raise_operation_error(
            request, "Can't submit or edit post in current ({}) complaint status".format(
                complaint.status
            )
        )


def validate_complaint_post_review_date(request, calendar=WORKING_DAYS, **kwargs):
    complaint = request.validated["complaint"]
    if complaint.status == "accepted":
        tender = request.validated["tender"]
        post_end_date = calculate_tender_business_date(
            complaint.reviewDate, -POST_SUBMIT_TIME,
            tender=tender, working_days=True, calendar=calendar
        )
        if get_now() > post_end_date:
            raise_operation_error(
                request,
                "Can submit or edit post not later than {duration.days} "
                "full business days before reviewDate".format(
                    duration=POST_SUBMIT_TIME
                )
            )


def validate_complaint_post_document_upload_by_author(request, **kwargs):
    if request.authenticated_role != request.context.author:
        request.errors.add("url", "role", "Can add document only by post author")
        request.errors.status = 403
        raise error_handler(request)


def validate_complaint_post(request, **kwargs):
    validate_tender_first_revision_date(request, validation_date=RELEASE_2020_04_19)
