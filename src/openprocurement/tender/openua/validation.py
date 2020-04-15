from datetime import timedelta

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.validation import (
    validate_data, validate_json_data, OPERATIONS, validate_accreditation_level,
    validate_accreditation_level_mode,
    validate_tender_first_revision_date,
)
from openprocurement.api.utils import (
    apply_data_patch, error_handler, get_now, raise_operation_error,
    update_logging_context,
    upload_objects_documents,
)
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.core.validation import validate_tender_period_extension, validate_patch_tender_data_draft
from openprocurement.tender.openua.constants import POST_SUBMIT_TIME


def validate_patch_tender_ua_data(request):
    data = validate_json_data(request)
    if request.context.status == "draft":
        validate_patch_tender_data_draft(request)
        return
    if data:
        if "items" in data:
            items = request.context.items
            cpv_group_lists = [i.classification.id[:3] for i in items]
            for item in data["items"]:
                if "classification" in item and "id" in item["classification"]:
                    cpv_group_lists.append(item["classification"]["id"][:3])
            if len(set(cpv_group_lists)) != 1:
                request.errors.add("body", "item", "Can't change classification")
                request.errors.status = 403
                raise error_handler(request.errors)
        if "enquiryPeriod" in data:
            if apply_data_patch(request.context.enquiryPeriod.serialize(), data["enquiryPeriod"]):
                request.errors.add("body", "item", "Can't change enquiryPeriod")
                request.errors.status = 403
                raise error_handler(request.errors)

    return validate_data(request, type(request.tender), True, data)


def validate_update_tender_document(request):
    status = request.validated["tender_status"]
    if status == "active.tendering":
        validate_tender_period_extension(request)


# bids
def validate_update_bid_to_draft(request):
    bid_status_to = request.validated["data"].get("status", request.context.status)
    if request.context.status != "draft" and bid_status_to == "draft":
        request.errors.add("body", "bid", "Can't update bid to ({}) status".format(bid_status_to))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_update_bid_to_active_status(request):
    bid_status_to = request.validated["data"].get("status", request.context.status)
    if bid_status_to != request.context.status and bid_status_to != "active":
        request.errors.add("body", "bid", "Can't update bid to ({}) status".format(bid_status_to))
        request.errors.status = 403
        raise error_handler(request.errors)


# bid documents
def validate_download_bid_document(request):
    if request.params.get("download"):
        document = request.validated["document"]
        authenticated_role = request.authenticated_role
        if document.confidentiality == "buyerOnly" and authenticated_role not in ("bid_owner", "tender_owner"):
            raise_operation_error(request, "Document download forbidden.")


def validate_bid_document_operation_in_award_status(request):
    if request.validated["tender_status"] in ("active.qualification", "active.awarded") and not any(
        award.status in ("pending", "active")
        for award in request.validated["tender"].awards
        if award.bid_id == request.validated["bid_id"]
    ):
        raise_operation_error(
            request,
            "Can't {} document because award of bid is not in pending or active state".format(
                OPERATIONS.get(request.method)
            ),
        )


def validate_update_bid_document_confidentiality(request):
    tender_status = request.validated["tender_status"]
    if tender_status != "active.tendering" and "confidentiality" in request.validated.get("data", {}):
        if request.context.confidentiality != request.validated["data"]["confidentiality"]:
            raise_operation_error(
                request,
                "Can't update document confidentiality in current ({}) tender status".format(tender_status),
            )


# complaint
def validate_submit_claim_time(request):
    tender = request.validated["tender"]
    claim_submit_time = request.content_configurator.tender_claim_submit_time
    if get_now() > calculate_tender_business_date(tender.tenderPeriod.endDate, -claim_submit_time, tender):
        raise_operation_error(
            request, "Can submit claim not later than {0.days} days before tenderPeriod end".format(claim_submit_time)
        )


def validate_update_claim_time(request):
    tender = request.validated["tender"]
    if get_now() > tender.enquiryPeriod.clarificationsUntil:
        raise_operation_error(request, "Can update claim only before enquiryPeriod.clarificationsUntil")


# complaint documents
def validate_complaint_document_operation_not_in_allowed_status(request):
    if request.validated["tender_status"] not in ["active.tendering"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


# contract
def validate_contract_update_with_accepted_complaint(request):
    tender = request.validated["tender"]
    if any(
        [
            any([c.status == "accepted" for c in i.complaints])
            for i in tender.awards
            if i.lotID in [a.lotID for a in tender.awards if a.id == request.context.awardID]
        ]
    ):
        raise_operation_error(request, "Can't update contract with accepted complaint")


def validate_accepted_complaints(request):
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
def validate_not_only_unsuccessful_awards_or_qualifications(request):
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
def validate_post_accreditation_level(request):
    tender = request.validated["tender"]
    levels = tender.edit_accreditations
    validate_accreditation_level(request, levels, "procurementMethodType", "post", "creation")
    mode = tender.get("mode", None)
    validate_accreditation_level_mode(request, mode, "procurementMethodType", "post", "creation")


def validate_complaint_post_data(request):
    update_logging_context(request, {"post_id": "__new__"})
    validate_post_accreditation_level(request)
    model = type(request.tender).complaints.model_class.posts.model_class
    post = validate_data(request, model)
    upload_objects_documents(
        request, request.validated["post"],
        route_kwargs={"post_id": request.validated["post"].id}
    )
    return post


def validate_award_complaint_post_data(request):
    update_logging_context(request, {"post_id": "__new__"})
    validate_post_accreditation_level(request)
    model = type(request.tender).awards.model_class.complaints.model_class.posts.model_class
    post = validate_data(request, model)
    upload_objects_documents(
        request, request.validated["post"],
        route_kwargs={"post_id": request.validated["post"].id}
    )
    return post


def validate_cancellation_complaint_post_data(request):
    update_logging_context(request, {"post_id": "__new__"})
    validate_post_accreditation_level(request)
    model = type(request.tender).cancellations.model_class.complaints.model_class.posts.model_class
    post = validate_data(request, model)
    upload_objects_documents(
        request, request.validated["post"],
        route_kwargs={"post_id": request.validated["post"].id}
    )
    return post


def validate_qualification_complaint_post_data(request):
    update_logging_context(request, {"post_id": "__new__"})
    validate_post_accreditation_level(request)
    model = type(request.tender).qualifications.model_class.complaints.model_class.posts.model_class
    post = validate_data(request, model)
    upload_objects_documents(
        request, request.validated["post"],
        route_kwargs={"post_id": request.validated["post"].id}
    )
    return post


def validate_complaint_post_complaint_status(request):
    complaint = request.validated["complaint"]
    if complaint.status not in ["pending", "accepted"]:
        raise_operation_error(
            request, "Can't submit or edit post in current ({}) complaint status".format(
                complaint.status
            )
        )


def validate_complaint_post_review_date(request):
    complaint = request.validated["complaint"]
    if complaint.status == "accepted":
        tender = request.validated["tender"]
        post_end_date = calculate_tender_business_date(complaint.reviewDate, -POST_SUBMIT_TIME, tender, True)
        if get_now() > post_end_date:
            raise_operation_error(
                request, "Can submit or edit post not later than {0.days} working days before reviewDate".format(
                    POST_SUBMIT_TIME
                )
            )


def validate_complaint_post_document_upload_by_author(request):
    if request.authenticated_role != request.context.author:
        request.errors.add("url", "role", "Can add document only by post author")
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_complaint_post(request):
    validate_tender_first_revision_date(request, validation_date=RELEASE_2020_04_19)
