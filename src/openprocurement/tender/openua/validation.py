from openprocurement.api.validation import validate_data, validate_json_data, OPERATIONS
from openprocurement.api.utils import apply_data_patch, error_handler, get_now, raise_operation_error
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.core.validation import validate_tender_period_extension, validate_patch_tender_data_draft


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
