from openprocurement.api.validation import validate_data, validate_json_data, OPERATIONS
from openprocurement.api.utils import (
    apply_data_patch, update_logging_context, error_handler, raise_operation_error,
)
from openprocurement.tender.competitivedialogue.models import STAGE2_STATUS
from openprocurement.tender.competitivedialogue.utils import (
    prepare_shortlistedFirms,
    prepare_author,
    prepare_bid_identifier,
    get_item_by_id,
)
from openprocurement.tender.core.validation import (
    _validate_complaint_accreditation_level,
    _validate_question_accreditation_level,
    validate_tender_document_update_not_by_author_or_tender_owner,
)
from openprocurement.tender.openua.validation import (
    validate_update_tender_document as validate_update_tender_document_base
)


def validate_patch_tender_stage2_data(request, **kwargs):
    data = validate_json_data(request)
    if request.context.status == "draft":
        default_statuses = ["active.tendering", STAGE2_STATUS]
        if "status" in data and data.get("status") not in default_statuses:
            raise_operation_error(request, "Can't update tender in current ({0}) status".format(data["status"]))
        request.validated["data"] = {"status": data.get("status")}
        request.context.status = data.get("status")
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
                raise error_handler(request)
        if "enquiryPeriod" in data:
            if apply_data_patch(request.context.enquiryPeriod.serialize(), data["enquiryPeriod"]):
                request.errors.add("body", "item", "Can't change enquiryPeriod")
                request.errors.status = 403
                raise error_handler(request)
    if request.context.status == STAGE2_STATUS and data.get("status") == "active.tendering":
        data = validate_data(request, type(request.tender), True, data)
        if data:  # if no error then add status to validate data
            request.context.status = "active.tendering"
            data["status"] = "active.tendering"
    else:
        data = validate_data(request, type(request.tender), True, data)

    return data


def validate_update_tender_document(request, **kwargs):
    status = request.validated["tender_status"]
    role = request.authenticated_role
    statuses = ["active.tendering", STAGE2_STATUS]
    auction_statuses = ["active.auction", "active.qualification"]
    if role != "auction" and status not in statuses or role == "auction" and status not in auction_statuses:
        raise_operation_error(
            request, "Can't {} document in current ({}) tender status".format(OPERATIONS.get(request.method), status)
        )
        validate_update_tender_document_base(request)
    if request.method in ["PUT", "PATCH"]:
        validate_tender_document_update_not_by_author_or_tender_owner(request)


def validate_author(request, shortlistedFirms, obj):
    """ Compare author key and key from shortlistedFirms """
    firms_keys = prepare_shortlistedFirms(shortlistedFirms)
    author_key = prepare_author(obj)
    if obj.get("questionOf") == "item":  # question can create on item
        if shortlistedFirms[0].get("lots"):
            item_id = author_key.split("_")[-1]
            item = get_item_by_id(request.validated["tender"], item_id)
            author_key = author_key.replace(author_key.split("_")[-1], item["relatedLot"])
        else:
            author_key = "_".join(author_key.split("_")[:-1])
    for firm in firms_keys:
        if author_key in firm:  # if we found legal firm then check another complaint
            break
    else:  # we didn't find legal firm, then return error
        error_message = "Author can't {} {}".format(
            "create" if request.method == "POST" else "patch", obj.__class__.__name__.lower()
        )
        request.errors.add("body", "author", error_message)
        request.errors.status = 403
        # return False
        raise error_handler(request)
    return True


def validate_complaint_data_stage2(request, **kwargs):
    update_logging_context(request, {"complaint_id": "__new__"})
    _validate_complaint_accreditation_level(request)
    json_data = validate_json_data(request)
    model = type(request.tender).complaints.field.find_model(json_data)
    data = validate_data(request, model)
    if data:
        if validate_author(request, request.tender["shortlistedFirms"], request.validated["complaint"]):
            return data  # validate is OK
        else:
            return None  # we catch errors
    return data


def validate_patch_complaint_data_stage2(request, **kwargs):
    model = type(request.context)
    data = validate_data(request, model, True)
    if data:
        if validate_author(request, request.tender["shortlistedFirms"], request.validated["complaint"]):
            return data  # validate is OK
        else:
            return None  # we catch errors
    return data


def validate_post_question_data_stage2(request, **kwargs):
    update_logging_context(request, {"question_id": "__new__"})
    _validate_question_accreditation_level(request)
    model = type(request.tender).questions.model_class
    data = validate_data(request, model)
    if data:
        if validate_author(request, request.tender["shortlistedFirms"], request.validated["question"]):
            return data  # validate is OK
        else:
            return None  # we catch errors
    return data


# tender
def validate_credentials_generation(request, **kwargs):
    if request.validated["tender"].status != "draft.stage2":
        raise_operation_error(
            request,
            "Can't generate credentials in current ({}) contract status".format(request.validated["tender"].status),
        )


def validate_tender_update(request, **kwargs):
    tender = request.context
    data = request.validated["data"]
    if (
        request.authenticated_role == "tender_owner"
        and "status" in data
        and tender["status"] not in ('draft',)
        and data["status"] not in ["active.pre-qualification.stand-still", "active.stage2.waiting", tender.status]
    ):
        raise_operation_error(request, "Can't update tender status")


# bid
def validate_bid_status_update_not_to_pending_or_draft(request, **kwargs):
    if request.authenticated_role != "Administrator":
        bid_status_to = request.validated["data"].get("status", request.context.status)
        bid_status_from = request.validated["bid"].get("status")
        if bid_status_from == bid_status_to:
            return
        if bid_status_to not in ["pending", "draft"]:
            request.errors.add("body", "bid", "Can't update bid to ({}) status".format(bid_status_to))
            request.errors.status = 403
            raise error_handler(request)


def validate_firm_to_create_bid(request, **kwargs):
    tender = request.validated["tender"]
    bid = request.validated["bid"]
    firm_keys = prepare_shortlistedFirms(tender.shortlistedFirms)
    bid_keys = prepare_bid_identifier(bid)
    if not (bid_keys <= firm_keys):
        raise_operation_error(request, "Firm can't create bid")


# lot
def validate_lot_operation_for_stage2(request, **kwargs):
    operations = {"POST": "create", "PATCH": "update", "DELETE": "delete"}
    raise_operation_error(request, "Can't {} lot for tender stage2".format(operations.get(request.method)))
