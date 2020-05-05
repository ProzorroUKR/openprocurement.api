# -*- coding: utf-8 -*-
from collections import defaultdict
from decimal import Decimal, ROUND_UP

from schematics.types import BaseType

from openprocurement.api.validation import (
    validate_data,
    validate_json_data,
    validate_accreditation_level,
    validate_accreditation_level_mode,
    OPERATIONS,
    validate_accreditation_level_kind,
    validate_tender_first_revision_date,
)
from openprocurement.api.constants import (
    SANDBOX_MODE,
    UA_ROAD_SCHEME,
    UA_ROAD_CPV_PREFIXES,
    GMDN_SCHEME,
    ATC_SCHEME,
    INN_SCHEME,
    GMDN_CPV_PREFIXES,
    RELEASE_2020_04_19
)
from openprocurement.api.utils import (
    get_now,
    is_ua_road_classification,
    is_gmdn_classification,
    to_decimal,
    update_logging_context,
    error_handler,
    raise_operation_error,
    check_document_batch,
    handle_data_exceptions,
    get_first_revision_date,
)
from openprocurement.tender.core.constants import AMOUNT_NET_COEF, FIRST_STAGE_PROCUREMENT_TYPES
from openprocurement.tender.core.utils import calculate_tender_business_date, requested_fields_changes
from openprocurement.planning.api.utils import extract_plan_adapter
from schematics.exceptions import ValidationError


def validate_tender_data(request):
    update_logging_context(request, {"tender_id": "__new__"})
    data = validate_json_data(request)
    model = request.tender_from_data(data, create=False)
    validate_tender_accreditation_level(request, model)
    validate_tender_accreditation_level_central(request, model)
    data = validate_data(request, model, data=data)
    validate_tender_accreditation_level_mode(request)
    validate_tender_kind(request, model)
    return data


def validate_tender_accreditation_level(request, model):
    levels = model.create_accreditations
    validate_accreditation_level(request, levels, "procurementMethodType", "tender", "creation")


def validate_tender_accreditation_level_central(request, model):
    data = request.validated["json_data"]
    kind = data.get("procuringEntity", {}).get("kind", "")
    levels = model.central_accreditations
    validate_accreditation_level_kind(request, levels, kind, "procurementMethodType", "tender", "creation")


def validate_tender_accreditation_level_mode(request):
    data = request.validated["data"]
    mode = data.get("mode", None)
    validate_accreditation_level_mode(request, mode, "procurementMethodType", "tender", "creation")


def validate_tender_kind(request, model):
    data = request.validated["data"]
    kind = data.get("procuringEntity", {}).get("kind", "")
    if kind not in model.procuring_entity_kinds:
        request.errors.add(
            "procuringEntity", "kind",
            "{kind!r} procuringEntity cannot publish this type of procedure. Only {kinds} are allowed.".format(
                kind=kind, kinds=", ".join(model.procuring_entity_kinds)
            )
        )
        request.errors.status = 403


def validate_patch_tender_data_draft(request):
    data = request.validated["json_data"]
    default_status = type(request.tender).fields["status"].default
    if data and data.get("status") != default_status:
        raise_operation_error(request, "Can't update tender in current (draft) status")
    request.validated["data"] = {"status": default_status}
    request.context.status = default_status


def validate_patch_tender_data(request):
    data = validate_json_data(request)
    if request.context.status == "draft":
        validate_patch_tender_data_draft(request)
        return
    return validate_data(request, type(request.tender), True, data)


def validate_tender_auction_data(request):
    data = validate_patch_tender_data(request)
    tender = request.validated["tender"]
    if tender.status != "active.auction":
        raise_operation_error(
            request,
            "Can't {} in current ({}) tender status".format(
                "report auction results" if request.method == "POST" else "update auction urls", tender.status
            ),
        )
    lot_id = request.matchdict.get("auction_lot_id")
    if tender.lots and any([i.status != "active" for i in tender.lots if i.id == lot_id]):
        raise_operation_error(
            request,
            "Can {} only in active lot status".format(
                "report auction results" if request.method == "POST" else "update auction urls"
            ),
        )
    if data is not None:
        bids = data.get("bids", [])
        tender_bids_ids = [i.id for i in tender.bids]
        if len(bids) != len(tender.bids):
            request.errors.add("body", "bids", "Number of auction results did not match the number of tender bids")
            request.errors.status = 422
            raise error_handler(request.errors)
        if set([i["id"] for i in bids]) != set(tender_bids_ids):
            request.errors.add("body", "bids", "Auction bids should be identical to the tender bids")
            request.errors.status = 422
            raise error_handler(request.errors)
        data["bids"] = [x for (y, x) in sorted(zip([tender_bids_ids.index(i["id"]) for i in bids], bids))]
        if data.get("lots"):
            tender_lots_ids = [i.id for i in tender.lots]
            if len(data.get("lots", [])) != len(tender.lots):
                request.errors.add("body", "lots", "Number of lots did not match the number of tender lots")
                request.errors.status = 422
                raise error_handler(request.errors)
            if set([i["id"] for i in data.get("lots", [])]) != set([i.id for i in tender.lots]):
                request.errors.add("body", "lots", "Auction lots should be identical to the tender lots")
                request.errors.status = 422
                raise error_handler(request.errors)
            data["lots"] = [
                x if x["id"] == lot_id else {}
                for (y, x) in sorted(
                    zip([tender_lots_ids.index(i["id"]) for i in data.get("lots", [])], data.get("lots", []))
                )
            ]
        if tender.lots:
            for index, bid in enumerate(bids):
                if (getattr(tender.bids[index], "status", "active") or "active") == "active":
                    if len(bid.get("lotValues", [])) != len(tender.bids[index].lotValues):
                        request.errors.add(
                            "body",
                            "bids",
                            [
                                {
                                    u"lotValues": [
                                        u"Number of lots of auction results did not match the number of tender lots"
                                    ]
                                }
                            ],
                        )
                        request.errors.status = 422
                        raise error_handler(request.errors)
                    for lot_index, lotValue in enumerate(tender.bids[index].lotValues):
                        if lotValue.relatedLot != bid.get("lotValues", [])[lot_index].get("relatedLot", None):
                            request.errors.add(
                                "body",
                                "bids",
                                [{u"lotValues": [{u"relatedLot": ["relatedLot should be one of lots of bid"]}]}],
                            )
                            request.errors.status = 422
                            raise error_handler(request.errors)
            for bid_index, bid in enumerate(data["bids"]):
                if "lotValues" in bid:
                    bid["lotValues"] = [
                        x
                        if x["relatedLot"] == lot_id
                        and (getattr(tender.bids[bid_index].lotValues[lotValue_index], "status", "active") or "active")
                        == "active"
                        else {}
                        for lotValue_index, x in enumerate(bid["lotValues"])
                    ]

    else:
        data = {}
    if request.method == "POST":
        now = get_now().isoformat()
        if (
            SANDBOX_MODE
            and tender.submissionMethodDetails
            and tender.submissionMethodDetails in [u"quick(mode:no-auction)", u"quick(mode:fast-forward)"]
        ):
            if tender.lots:
                data["lots"] = [
                    {"auctionPeriod": {"startDate": now, "endDate": now}} if i.id == lot_id else {} for i in tender.lots
                ]
            else:
                data["auctionPeriod"] = {"startDate": now, "endDate": now}
        else:
            if tender.lots:
                data["lots"] = [{"auctionPeriod": {"endDate": now}} if i.id == lot_id else {} for i in tender.lots]
            else:
                data["auctionPeriod"] = {"endDate": now}
    request.validated["data"] = data


def validate_bid_data(request):
    update_logging_context(request, {"bid_id": "__new__"})
    validate_bid_accreditation_level(request)
    model = type(request.tender).bids.model_class
    bid = validate_data(request, model)
    validated_bid = request.validated.get("bid")
    if validated_bid:
        if any([key == "documents" or "Documents" in key for key in validated_bid.keys()]):
            bid_documents = validate_bid_documents(request)
            if not bid_documents:
                return
            for documents_type, documents in bid_documents.items():
                validated_bid[documents_type] = documents
    return bid


def validate_bid_accreditation_level(request):
    tender = request.validated["tender"]
    levels = tender.edit_accreditations
    validate_accreditation_level(request, levels, "procurementMethodType", "bid", "creation")
    mode = tender.get("mode", None)
    validate_accreditation_level_mode(request, mode, "procurementMethodType", "bid", "creation")


def validate_bid_documents(request):
    bid_documents = [key for key in request.validated["bid"].keys() if key == "documents" or "Documents" in key]
    documents = {}
    for doc_type in bid_documents:
        documents[doc_type] = []
        for document in request.validated["bid"][doc_type]:
            model = getattr(type(request.validated["bid"]), doc_type).model_class
            document = model(document)
            document.validate()
            route_kwargs = {"bid_id": request.validated["bid"].id}
            document = check_document_batch(request, document, doc_type, route_kwargs)
            documents[doc_type].append(document)
    return documents


def validate_patch_bid_data(request):
    model = type(request.tender).bids.model_class
    return validate_data(request, model, True)


def validate_award_data(request):
    update_logging_context(request, {"award_id": "__new__"})
    model = type(request.tender).awards.model_class
    return validate_data(request, model)


def validate_award_milestone_data(request):
    update_logging_context(request, {"milestone_id": "__new__"})
    model = type(request.tender).awards.model_class.milestones.model_class
    return validate_data(request, model)


def validate_qualification_milestone_data(request):
    update_logging_context(request, {"milestone_id": "__new__"})
    model = type(request.tender).qualifications.model_class.milestones.model_class
    return validate_data(request, model)


def _validate_item_milestone_24hours(request, item_name):
    milestone = request.validated["milestone"]
    item_class = getattr(type(request.tender), "{}s".format(item_name))
    model = item_class.model_class.milestones.model_class
    if milestone.code != model.CODE_24_HOURS:
        raise_operation_error(
            request,
            "The only allowed milestone code is '{}'".format(model.CODE_24_HOURS)
        )

    if request.context.status != "pending":
        raise_operation_error(
            request,
            "Not allowed in current '{}' {} status".format(
                request.context.status,
                request.context.__class__.__name__.lower()
            )
        )


def validate_award_milestone_24hours(request):
    return _validate_item_milestone_24hours(request, item_name="award")


def validate_qualification_milestone_24hours(request):
    return _validate_item_milestone_24hours(request, item_name="qualification")


def validate_award_milestone_released(request):
    validate_tender_first_revision_date(request, validation_date=RELEASE_2020_04_19)


def validate_patch_award_data(request):
    model = type(request.tender).awards.model_class
    return validate_data(request, model, True)


def validate_question_data(request):
    update_logging_context(request, {"question_id": "__new__"})
    validate_question_accreditation_level(request)
    model = type(request.tender).questions.model_class
    return validate_data(request, model)


def validate_question_accreditation_level(request):
    tender = request.validated["tender"]
    levels = tender.edit_accreditations
    validate_accreditation_level(request, levels, "procurementMethodType", "question", "creation")
    mode = tender.get("mode", None)
    validate_accreditation_level_mode(request, mode, "procurementMethodType", "question", "creation")


def validate_patch_question_data(request):
    model = type(request.tender).questions.model_class
    return validate_data(request, model, True)


def validate_question_update_with_cancellation_lot_pending(request):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())
    question = request.validated["question"]

    if tender_created < RELEASE_2020_04_19 or question.questionOf != "lot":
        return

    accept_lot = all([
        any([j.status == "resolved" for j in i.complaints])
        for i in tender.cancellations
        if i.status == "unsuccessful" and getattr(i, "complaints", None) and i.relatedLot == question.relatedItem
    ])

    if (
        request.authenticated_role == "tender_owner"
        and (
            any([
                i for i in tender.cancellations
                if i.relatedLot and i.status == "pending" and i.relatedLot == question.relatedItem])
            or not accept_lot
        )
    ):
        raise_operation_error(
            request,
            "Can't update question with pending cancellation",
        )


def validate_complaint_data(request):
    update_logging_context(request, {"complaint_id": "__new__"})
    validate_complaint_accreditation_level(request)
    if "cancellation" in request.validated:
        model = type(request.validated["cancellation"]).complaints.model_class
    else:
        model = type(request.tender).complaints.model_class
    return validate_data(request, model)


def validate_complaint_accreditation_level(request):
    tender = request.validated["tender"]
    levels = tender.edit_accreditations
    validate_accreditation_level(request, levels, "procurementMethodType", "complaint", "creation")
    mode = tender.get("mode", None)
    validate_accreditation_level_mode(request, mode, "procurementMethodType", "complaint", "creation")


def validate_patch_complaint_data(request):
    if "cancellation" in request.validated:
        model = type(request.validated["cancellation"]).complaints.model_class
    else:
        model = type(request.tender).complaints.model_class
    return validate_data(request, model, True)


def validate_cancellation_data(request):
    update_logging_context(request, {"cancellation_id": "__new__"})
    model = type(request.tender).cancellations.model_class
    return validate_data(request, model)


def validate_patch_cancellation_data(request):
    model = type(request.tender).cancellations.model_class
    return validate_data(request, model, True)

# Cancellation

def validate_cancellation_operation_document(request):
    tender = request.validated["tender"]

    if get_first_revision_date(tender, default=get_now()) < RELEASE_2020_04_19:
        return

    cancellation = request.validated["cancellation"]

    if not (
        cancellation.status == "draft"
        or (cancellation.status == "pending"
            and any([i for i in cancellation.complaints if i.status == "satisfied"]))
    ):
        raise_operation_error(
            request,
            "Document can't be {} in current({}) cancellation status".format(
                OPERATIONS.get(request.method), cancellation.status)
        )


def validate_cancellation_status_with_complaints(request):
    cancellation = request.context

    if get_first_revision_date(request.tender, default=get_now()) < RELEASE_2020_04_19:
        return

    curr_status = cancellation.status
    data = request.validated["data"]
    new_status = data.get("status")

    status_map = {
        "draft": ("pending", "unsuccessful", "draft"),
        "pending": ("unsuccessful", "pending"),
    }

    available_statuses = status_map.get(curr_status)
    error_msg = u"Cancellation can't be updated from {} to {} status"

    if not available_statuses:
        raise_operation_error(
            request,
            u"Can't update cancellation in current ({}) status".format(curr_status)
        )

    if new_status not in available_statuses:
        raise_operation_error(
            request,
            error_msg.format(curr_status, new_status),
            status=422
        )

    if (
        new_status == "pending"
        and (
            not cancellation.reason
            or not cancellation.cancellationOf
            or not cancellation.documents
        )
    ):
        raise_operation_error(
            request,
            u"Fields reason, cancellationOf and documents must be filled for switch cancellation to pending status",
            status=422,
        )

    if (
        curr_status == "pending"
        and new_status == "unsuccessful"
        and not any([i.status == "satisfied" for i in cancellation.complaints])
    ):
        raise_operation_error(
            request,
            error_msg.format(curr_status, new_status),
            status=422
        )


def validate_cancellation_status_without_complaints(request):
    cancellation = request.context

    if get_first_revision_date(request.tender, default=get_now()) < RELEASE_2020_04_19:
        return
    curr_status = cancellation.status
    new_status = request.validated["data"].get("status")

    status_map = {"draft": ("active", "unsuccessful", "draft")}
    available_statuses = status_map.get(curr_status)

    if not available_statuses:
        raise_operation_error(
            request,
            u"Can't update cancellation in current ({}) status".format(curr_status)
        )

    if new_status not in available_statuses:
        raise_operation_error(
            request,
            u"Cancellation can't be updated from %s to %s status" % (curr_status, new_status),
            status=422,
        )

    if (
        new_status == "active"
        and (
            not cancellation.reason
            or not cancellation.cancellationOf
            or not cancellation.documents
        )
    ):
        raise_operation_error(
            request,
            u"Fields reason, cancellationOf and documents must be filled for switch cancellation to active status",
            status=422,
        )


def validate_operation_cancellation_in_complaint_period(request):
    tender = request.validated["tender"]
    now = get_now()
    tender_created = get_first_revision_date(tender, default=now)

    if tender_created < RELEASE_2020_04_19:
        return
    msg = "Cancellation can't be {} when exists active complaint period".format(OPERATIONS.get(request.method))

    if tender.status in ["active.pre-qualification.stand-still"]:
        raise_operation_error(request, msg)

    cancellation = (
        request.validated["cancellation"]
        if "cancellation" in request.validated
        else request.validated["data"]
    )

    relatedLot = cancellation.get("relatedLot")
    complaint_statuses = ["pending", "accepted", "satisfied"]

    if not relatedLot:
        if any(i.status in complaint_statuses for i in tender.get("complaints", [])):
            raise_operation_error(request, msg)

        if any(
            i for i in tender.awards
            if i.get("complaintPeriod")
                and i.complaintPeriod.endDate
                and i.complaintPeriod.startDate < get_now() < i.complaintPeriod.endDate
        ):
            raise_operation_error(request, msg)
    else:
        if any(
                i.status in complaint_statuses
                for i in tender.get("complaints", [])
                if relatedLot == i.get("relatedLot")
        ):
            raise_operation_error(request, msg)

        if any(
            i for i in tender.awards
            if relatedLot == i.get("lotID")
                and i.get("complaintPeriod")
                and i.complaintPeriod.endDate
                and i.complaintPeriod.startDate < get_now() < i.complaintPeriod.endDate
        ):
            raise_operation_error(request, msg)


# Cancellation complaint
def validate_cancellation_complaint(request):
    old_rules = get_first_revision_date(request.tender, default=get_now()) < RELEASE_2020_04_19
    tender = request.validated["tender"]
    without_complaints = ["belowThreshold", "reporting", "closeFrameworkAgreementSelectionUA"]
    if old_rules or tender.procurementMethodType in without_complaints:
        raise_operation_error(request, "Not Found", status=404)


def validate_cancellation_complaint_add_only_in_pending(request):

    cancellation = request.validated["cancellation"]
    complaint_period = cancellation.complaintPeriod
    if cancellation.status != "pending":
        raise_operation_error(
            request,
            u"Complaint can be add only in pending status of cancellation",
            status=422,
        )

    is_complaint_period = (
        complaint_period.startDate <= get_now() <= complaint_period.endDate
        if complaint_period
        else False
    )
    if cancellation.status == "pending" and not is_complaint_period:
        raise_operation_error(
            request,
            u"Complaint can't be add after finish of complaint period",
            status=422,
        )


def validate_cancellation_complaint_only_one(request):
    cancellation = request.validated["cancellation"]
    complaints = cancellation.complaints
    if (
        complaints
        and complaints[-1].status not in ["invalid", "declined",  "cancelled", "pending"]
    ):
        raise_operation_error(
            request,
            u"Cancellation can have only one active complaint",
            status=422,
        )


def validate_cancellation_complaint_resolved(request):
    cancellation = request.validated["cancellation"]
    complaint = request.validated["data"]
    if complaint.get("tendererAction") and cancellation.status != "unsuccessful":
        raise_operation_error(
            request,
            u"Complaint can't have tendererAction only if cancellation not in unsuccessful status",
            status=422,
        )


def validate_contract_data(request):
    update_logging_context(request, {"contract_id": "__new__"})
    model = type(request.tender).contracts.model_class
    return validate_data(request, model)


def validate_patch_contract_data(request):
    model = type(request.tender).contracts.model_class
    return validate_data(request, model, True)


def validate_lot_data(request):
    update_logging_context(request, {"lot_id": "__new__"})
    model = type(request.tender).lots.model_class
    return validate_data(request, model)


def validate_patch_lot_data(request):
    model = type(request.tender).lots.model_class
    return validate_data(request, model, True)


def validate_relatedlot(tender, relatedLot):
    if relatedLot not in [lot.id for lot in tender.lots if lot]:
        raise ValidationError(u"relatedLot should be one of lots")


def validate_lotvalue_value(tender, relatedLot, value):
    if not value and not relatedLot:
        return
    lot = next((lot for lot in tender.lots if lot and lot.id == relatedLot), None)
    if not lot:
        return
    if lot.value.amount < value.amount:
        raise ValidationError(u"value of bid should be less than value of lot")
    if lot.get("value").currency != value.currency:
        raise ValidationError(u"currency of bid should be identical to currency of value of lot")
    if lot.get("value").valueAddedTaxIncluded != value.valueAddedTaxIncluded:
        raise ValidationError(
            u"valueAddedTaxIncluded of bid should be identical " u"to valueAddedTaxIncluded of value of lot"
        )


def validate_bid_value(tender, value):
    if tender.lots:
        if value:
            raise ValidationError(u"value should be posted for each lot of bid")
    else:
        if not value:
            raise ValidationError(u"This field is required.")
        if tender.value.amount < value.amount:
            raise ValidationError(u"value of bid should be less than value of tender")
        if tender.get("value").currency != value.currency:
            raise ValidationError(u"currency of bid should be identical to currency of value of tender")
        if tender.get("value").valueAddedTaxIncluded != value.valueAddedTaxIncluded:
            raise ValidationError(
                u"valueAddedTaxIncluded of bid should be identical " u"to valueAddedTaxIncluded of value of tender"
            )


def validate_minimalstep(data, value):
    if value and value.amount and data.get("value"):
        if data.get("value").amount < value.amount:
            raise ValidationError(u"value should be less than value of tender")
        if data.get("value").currency != value.currency:
            raise ValidationError(u"currency should be identical to currency of value of tender")
        if data.get("value").valueAddedTaxIncluded != value.valueAddedTaxIncluded:
            raise ValidationError(
                u"valueAddedTaxIncluded should be identical " u"to valueAddedTaxIncluded of value of tender"
            )


# cancellation
def validate_cancellation_of_active_lot(request):
    tender = request.validated["tender"]
    cancellation = request.validated["cancellation"]
    if any(lot.status != "active"
           for lot in getattr(tender, "lots", "")
           if lot.id == cancellation.relatedLot):
        raise_operation_error(request, "Can perform cancellation only in active lot status")


def validate_operation_cancellation_permission(request):

    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())

    if tender_created < RELEASE_2020_04_19:
        return

    if "cancellation" in request.validated:
        cancellation = request.validated["cancellation"]
    else:
        cancellation = request.validated["data"]

    if cancellation.get("relatedLot"):
        relatedLot = cancellation.get("relatedLot")
        if (
            cancellation.get("status") != "pending"
            and any(i for i in tender.cancellations if i.status == "pending" and i.get("relatedLot") == relatedLot)
        ):
            raise_operation_error(request, "Forbidden")
    else:

        if (
            cancellation.get("status") != "pending"
            and any(i for i in tender.cancellations if i.status == "pending")
        ):
            raise_operation_error(request, "Forbidden")


def validate_create_cancellation_in_active_auction(request):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())

    if tender_created > RELEASE_2020_04_19 and tender.status in ["active.auction"]:
        raise_operation_error(
            request, "Can't create cancellation in current ({}) tender status". format(tender.status))


# tender
def validate_tender_not_in_terminated_status(request):
    tender = request.validated["tender"]
    tender_status = tender.status
    term_statuses = ("complete", "unsuccessful", "cancelled", "draft.unsuccessful")
    if request.authenticated_role != "Administrator" and tender_status in term_statuses:
        raise_operation_error(request, "Can't update tender in current ({}) status".format(tender_status))


def validate_absence_of_pending_accepted_satisfied_complaints(request, cancellation=None):
    """
    Disallow cancellation of tenders and lots that have any complaints in affected statuses
    """
    tender = request.validated["tender"]
    tender_creation_date = get_first_revision_date(tender, default=get_now())
    if tender_creation_date < RELEASE_2020_04_19:
        return

    if not cancellation:
        cancellation = request.validated["cancellation"]
    cancellation_lot = cancellation.get("relatedLot")

    def validate_complaint(complaint, complaint_lot, item_name):
        """
        raise error if it's:
         - canceling tender that has a complaint (not cancellation_lot)
         - canceling tender that has a lot complaint (not cancellation_lot)
         - canceling lot that has a lot complaint (cancellation_lot == complaint_lot)
         - canceling lot if there is a non-lot complaint (not complaint_lot)
        AND complaint.status is in ("pending", "accepted", "satisfied")
        """
        if not cancellation_lot or not complaint_lot or cancellation_lot == complaint_lot:
            if complaint.get("status") in ("pending", "accepted", "satisfied"):
                raise_operation_error(
                    request,
                    "Can't perform operation for there is {} complaint in {} status".format(
                        item_name, complaint.get("status"))
                )

    for c in tender.get("complaints", ""):
        validate_complaint(c, c.get("relatedLot"), "a tender")

    for qualification in tender.get("qualifications", ""):
        for c in qualification.get("complaints", ""):
            validate_complaint(c, qualification.get("lotID"), "a qualification")

    for award in tender.get("awards", ""):
        for c in award.get("complaints", ""):
            validate_complaint(c, award.get("lotID"), "an award")


def validate_tender_change_status_with_cancellation_lot_pending(request):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())
    data = request.validated["data"]
    new_status = data.get("status", tender.status)

    if (
        tender_created < RELEASE_2020_04_19
        or not tender.lots
        or tender.status == new_status
    ):
        return

    accept_lot = all([
        any([j.status == "resolved" for j in i.complaints])
        for i in tender.cancellations
        if i.status == "unsuccessful" and getattr(i, "complaints", None) and i.relatedLot
    ])

    if (
        request.authenticated_role == "tender_owner"
        and (
            any([
                i for i in tender.cancellations
                if i.relatedLot and i.status == "pending"])
            or not accept_lot
        )
    ):
        raise_operation_error(
            request,
            "Can't update tender with pending cancellation in one of exists lot",
        )


def validate_tender_status_update_not_in_pre_qualificaton(request):
    tender = request.context
    data = request.validated["data"]
    if (
        request.authenticated_role == "tender_owner"
        and "status" in data
        and data["status"] not in ["active.pre-qualification.stand-still", tender.status]
    ):
        raise_operation_error(request, "Can't update tender status")


def validate_tender_period_extension(request):
    extra_period = request.content_configurator.tendering_period_extra
    tender = request.validated["tender"]
    if calculate_tender_business_date(get_now(), extra_period, tender) > tender.tenderPeriod.endDate:
        raise_operation_error(request, "tenderPeriod should be extended by {0.days} days".format(extra_period))


# tender documents
def validate_document_operation_in_not_allowed_period(request):
    if (
        request.authenticated_role != "auction"
        and request.validated["tender_status"] != "active.tendering"
        or request.authenticated_role == "auction"
        and request.validated["tender_status"] not in ["active.auction", "active.qualification"]
    ):
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_tender_document_update_not_by_author_or_tender_owner(request):
    if request.authenticated_role != (request.context.author or "tender_owner"):
        request.errors.add("url", "role", "Can update document only author")
        request.errors.status = 403
        raise error_handler(request.errors)


# bids
def validate_bid_operation_not_in_tendering(request):
    if request.validated["tender_status"] != "active.tendering":
        operation = "add" if request.method == "POST" else "delete"
        if request.authenticated_role != "Administrator" and request.method in ("PUT", "PATCH"):
            operation = "update"
        raise_operation_error(
            request, "Can't {} bid in current ({}) tender status".format(operation, request.validated["tender_status"])
        )


def validate_bid_document_in_tender_status(request):
    """
    active.tendering - tendering docs
    active.awarded - qualification docs that should be posted into award (another temp solution)
    """
    if request.validated["tender_status"] not in (
        "active.tendering",
        "active.awarded",
    ):
        operation = OPERATIONS.get(request.method)
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(operation, request.validated["tender_status"])
        )


def validate_bid_operation_period(request):
    tender = request.validated["tender"]
    if (
        tender.tenderPeriod.startDate
        and get_now() < tender.tenderPeriod.startDate
        or get_now() > tender.tenderPeriod.endDate
    ):
        operation = "added" if request.method == "POST" else "deleted"
        if request.authenticated_role != "Administrator" and request.method in ("PUT", "PATCH"):
            operation = "updated"
        raise_operation_error(
            request,
            "Bid can be {} only during the tendering period: from ({}) to ({}).".format(
                operation,
                tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.isoformat(),
                tender.tenderPeriod.endDate.isoformat(),
            ),
        )


def validate_update_deleted_bid(request):
    if request.context.status == "deleted":
        raise_operation_error(request, "Can't update bid in ({}) status".format(request.context.status))


def validate_bid_status_update_not_to_pending(request):
    if request.authenticated_role != "Administrator":
        bid_status_to = request.validated["data"].get("status", request.context.status)
        if bid_status_to != "pending":
            raise_operation_error(request, "Can't update bid to ({}) status".format(bid_status_to))


# bid document
def validate_bid_document_operation_period(request):
    tender = request.validated["tender"]
    if request.validated["tender_status"] == "active.tendering" and (
        tender.tenderPeriod.startDate
        and get_now() < tender.tenderPeriod.startDate
        or get_now() > tender.tenderPeriod.endDate
    ):
        raise_operation_error(
            request,
            "Document can be {} only during the tendering period: from ({}) to ({}).".format(
                "added" if request.method == "POST" else "updated",
                tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.isoformat(),
                tender.tenderPeriod.endDate.isoformat(),
            ),
        )


def validate_view_bid_document(request):
    tender_status = request.validated["tender_status"]
    if tender_status in ("active.tendering", "active.auction") and request.authenticated_role != "bid_owner":
        raise_operation_error(
            request,
            "Can't view bid documents in current ({}) tender status".format(tender_status),
        )


def validate_bid_document_operation_in_not_allowed_tender_status(request):
    if request.validated["tender_status"] not in ["active.tendering", "active.qualification"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_bid_document_operation_with_not_pending_award(request):
    if request.validated["tender_status"] == "active.qualification" and not any(
        award.status == "pending"
        for award in request.validated["tender"].awards
        if award.bid_id == request.validated["bid_id"]
    ):
        raise_operation_error(
            request,
            "Can't {} document because award of bid is not in pending state".format(OPERATIONS.get(request.method)),
        )


# for openua, openeu
def unless_allowed_by_qualification_milestone(validation):
    """
    decorator for 24hours and anomaly low price features to skip some view validator functions
    :param validation: a function runs unless it's disabled by an active qualification milestone
    :return:
    """
    def decorated_validation(request):
        tender = request.validated["tender"]
        bid_id = request.validated["bid"]["id"]
        if "qualifications" in tender:
            qualifications = [q for q in tender["qualifications"]
                              if q["status"] == "pending" and q["bidID"] == bid_id]
        else:
            qualifications = [q for q in tender.get("awards", "")
                              if q["status"] == "pending" and q["bid_id"] == bid_id]
        now = get_now()
        if qualifications and any(
                milestone["code"] in ("24h",) and milestone["date"] < now < milestone["dueDate"]
                for q in qualifications
                for milestone in q.get("milestones", "")
        ):
            return  # skipping the validation
        # else
        return validation(request)

    return decorated_validation


def validate_update_status_before_milestone_due_date(request):
    from openprocurement.tender.core.models import QualificationMilestone
    context = request.context
    sent_status = request.json_body.get("data", {}).get("status")
    if context.status == "pending" and context.status != sent_status:
        now = get_now()
        for milestone in context.milestones:
            if (
                milestone.code == QualificationMilestone.CODE_24_HOURS
                and milestone["date"] < now < milestone["dueDate"]
            ):
                raise_operation_error(
                    request,
                    "Can't change status to '{}' until milestone.dueDate: {}".format(
                        sent_status,
                        milestone["dueDate"].isoformat()
                    ),
                )


# lots
def validate_lot_operation_not_in_allowed_status(request):
    tender = request.validated["tender"]
    if tender.status not in ["active.tendering"]:
        raise_operation_error(
            request, "Can't {} lot in current ({}) tender status".format(OPERATIONS.get(request.method), tender.status)
        )


# complaints
def validate_complaint_operation_not_in_active_tendering(request):
    tender = request.validated["tender"]
    if tender.status != "active.tendering":
        raise_operation_error(
            request,
            "Can't {} complaint in current ({}) tender status".format(OPERATIONS.get(request.method), tender.status),
        )


def validate_complaint_update_with_cancellation_lot_pending(request):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())
    complaint = request.validated["complaint"]

    if tender_created < RELEASE_2020_04_19 or not complaint.relatedLot:
        return

    accept_lot = all([
        any([j.status == "resolved" for j in i.complaints])
        for i in tender.cancellations
        if i.status == "unsuccessful" and getattr(i, "complaints", None) and i.relatedLot == complaint.relatedLot
    ])

    if (
        request.authenticated_role == "tender_owner"
        and (
            any([
                i for i in tender.cancellations
                if i.relatedLot and i.status == "pending" and i.relatedLot == complaint.relatedLot])
            or not accept_lot
        )
    ):
        raise_operation_error(
            request,
            "Can't update complaint with pending cancellation lot".format(OPERATIONS.get(request.method)),
        )


def validate_submit_complaint_time(request):
    complaint_submit_time = request.content_configurator.tender_complaint_submit_time
    tender = request.validated["tender"]
    if get_now() > tender.complaintPeriod.endDate:
        raise_operation_error(
            request,
            "Can submit complaint not later than {0.days} days before tenderPeriod end".format(complaint_submit_time),
        )


# complaints document
def validate_status_and_role_for_complaint_document_operation(request):
    roles = request.content_configurator.allowed_statuses_for_complaint_operations_for_roles
    if request.validated["complaint"].status not in roles.get(request.authenticated_role, []):
        raise_operation_error(
            request,
            "Can't {} document in current ({}) complaint status".format(
                OPERATIONS.get(request.method), request.validated["complaint"].status
            ),
        )


def validate_complaint_document_update_not_by_author(request):
    if request.authenticated_role != request.context.author:
        request.errors.add("url", "role", "Can update document only author")
        request.errors.status = 403
        raise error_handler(request.errors)


# awards
def validate_update_award_with_cancellation_lot_pending(request):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())

    award = request.validated["award"]

    if tender_created < RELEASE_2020_04_19 or not award.lotID:
        return

    accept_lot = all([
        any([j.status == "resolved" for j in i.complaints])
        for i in tender.cancellations
        if i.status == "unsuccessful" and getattr(i, "complaints", None) and i.relatedLot == award.lotID
    ])

    if any([
        i for i in tender.cancellations
        if i.relatedLot and i.status == "pending" and i.relatedLot == award.lotID
    ]) or not accept_lot:
        raise_operation_error(request, "Can't update award with pending cancellation lot")


def validate_update_award_in_not_allowed_status(request):
    tender = request.validated["tender"]
    if tender.status not in ["active.qualification", "active.awarded"]:
        raise_operation_error(request, "Can't update award in current ({}) tender status".format(tender.status))


def validate_update_award_only_for_active_lots(request):
    tender = request.validated["tender"]
    award = request.context
    if any([i.status != "active" for i in tender.lots if i.id == award.lotID]):
        raise_operation_error(request, "Can update award only in active lot status")


def validate_update_award_with_accepted_complaint(request):
    tender = request.validated["tender"]
    award = request.context
    if any([any([c.status == "accepted" for c in i.complaints]) for i in tender.awards if i.lotID == award.lotID]):
        raise_operation_error(request, "Can't update award with accepted complaint")


# award complaint
def validate_award_complaint_operation_not_in_allowed_status(request):
    tender = request.validated["tender"]
    if tender.status not in ["active.qualification", "active.awarded"]:
        raise_operation_error(
            request,
            "Can't {} complaint in current ({}) tender status".format(OPERATIONS.get(request.method), tender.status),
        )


def validate_award_complaint_add_only_for_active_lots(request):
    tender = request.validated["tender"]
    if any([i.status != "active" for i in tender.lots if i.id == request.context.lotID]):
        raise_operation_error(request, "Can add complaint only in active lot status")


def validate_award_complaint_update_only_for_active_lots(request):
    tender = request.validated["tender"]
    if any([i.status != "active" for i in tender.lots if i.id == request.validated["award"].lotID]):
        raise_operation_error(request, "Can update complaint only in active lot status")


def validate_add_complaint_with_tender_cancellation_in_pending(request):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())

    if tender_created < RELEASE_2020_04_19:
        return

    if any([i for i in tender.cancellations if i.status == "pending" and not i.relatedLot]):
        raise_operation_error(request, "Can't add complaint if tender have cancellation in pending status")


def validate_add_complaint_with_lot_cancellation_in_pending(type_name):

    type_name = type_name.lower()

    def validation(request):
        fields_names = {
            "lot": "id",
            "award": "lotID",
            "qualification": "lotID",
            "complaint": "relatedLot",
        }
        tender = request.validated["tender"]
        tender_created = get_first_revision_date(tender, default=get_now())

        field = fields_names.get(type_name)
        o = request.validated.get(type_name)
        lot_id = getattr(o, field, None)

        if tender_created < RELEASE_2020_04_19 or not lot_id:
            return

        if any([
            i for i in tender.cancellations
            if i.relatedLot and i.status == "pending" and i.relatedLot == lot_id
        ]):
            raise_operation_error(
                request,
                "Can't add complaint to {} with 'pending' lot cancellation".format(type_name),
            )

    return validation


def validate_operation_with_lot_cancellation_in_pending(type_name):
    def validation(request):
        fields_names = {
            "lot": "id",
            "award": "lotID",
            "qualification": "lotID",
            "complaint": "relatedLot",
            "question": "relatedItem"
        }

        tender = request.validated["tender"]
        tender_created = get_first_revision_date(tender, default=get_now())

        field = fields_names.get(type_name)
        o = request.validated.get(type_name)
        lot_id = getattr(o, field, None)

        if tender_created < RELEASE_2020_04_19 or not lot_id:
            return

        msg = "Can't {} {} with lot that have active cancellation"
        if type_name == "lot":
            msg = "Can't {} lot that have active cancellation"

        accept_lot = all([
            any([j.status == "resolved" for j in i.complaints])
            for i in tender.cancellations
            if i.status == "unsuccessful" and getattr(i, "complaints", None) and i.relatedLot == lot_id
        ])

        if (
            request.authenticated_role == "tender_owner"
            and (
                any([
                    i for i in tender.cancellations
                    if i.relatedLot and i.status == "pending" and i.relatedLot == lot_id])
                or not accept_lot
            )
        ):
            raise_operation_error(
                request,
                msg.format(OPERATIONS.get(request.method), type_name),
            )
    return validation


def validate_add_complaint_not_in_complaint_period(request):
    period = request.context.complaintPeriod
    if period and (
        period.startDate and period.startDate > get_now()
        or period.endDate and period.endDate < get_now()
    ):
        raise_operation_error(request, "Can add complaint only in complaintPeriod")


def validate_update_cancellation_complaint_not_in_allowed_complaint_status(request):
    if request.context.status not in ["draft", "pending", "accepted", "satisfied", "stopping"]:
        raise_operation_error(request, "Can't update complaint in current ({}) status".format(request.context.status))


def validate_update_complaint_not_in_allowed_complaint_status(request):
    if request.context.status not in ["draft", "claim", "answered", "pending", "accepted", "satisfied", "stopping"]:
        raise_operation_error(request, "Can't update complaint in current ({}) status".format(request.context.status))


# award complaint document
def validate_award_complaint_document_operation_not_in_allowed_status(request):
    if request.validated["tender_status"] not in ["active.qualification", "active.awarded"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_award_complaint_document_operation_only_for_active_lots(request):
    if any(
        [i.status != "active" for i in request.validated["tender"].lots if i.id == request.validated["award"].lotID]
    ):
        raise_operation_error(
            request, "Can {} document only in active lot status".format(OPERATIONS.get(request.method))
        )


# contract
def validate_contract_operation_not_in_allowed_status(request):
    if request.validated["tender_status"] not in ["active.qualification", "active.awarded"]:
        raise_operation_error(
            request,
            "Can't {} contract in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_update_contract_only_for_active_lots(request):
    tender = request.validated["tender"]
    if any(
        [
            i.status != "active"
            for i in tender.lots
            if i.id in [a.lotID for a in tender.awards if a.id == request.context.awardID]
        ]
    ):
        raise_operation_error(request, "Can update contract only in active lot status")


def validate_update_contract_value(request, name="value", attrs=("currency",)):
    data = request.validated["data"]
    value = data.get(name)
    if value:
        for ro_attr in attrs:
            field = getattr(request.context, name)
            if field and value.get(ro_attr) != field.to_native().get(ro_attr):
                raise_operation_error(request, "Can't update {} for contract {}".format(ro_attr, name), name=name)


def validate_update_contract_value_net_required(request, name="value"):
    data = request.validated["data"]
    value = data.get(name)
    if value is not None and requested_fields_changes(request, (name, "status")):
        contract_amount_net = value.get("amountNet")
        if contract_amount_net is None:
            raise_operation_error(request, dict(amountNet=BaseType.MESSAGES["required"]), status=422, name=name)


def validate_update_contract_value_with_award(request):
    data = request.validated["data"]
    value = data.get("value")
    if value and requested_fields_changes(request, ("value", "status")):
        award = [award for award in request.validated["tender"].awards if award.id == request.context.awardID][0]
        amount = value.get("amount")
        amount_net = value.get("amountNet")
        tax_included = value.get("valueAddedTaxIncluded")

        if tax_included:
            if award.value.valueAddedTaxIncluded:
                if amount > award.value.amount:
                    raise_operation_error(request, "Amount should be less or equal to awarded amount", name="value")
            else:
                if amount_net > award.value.amount:
                    raise_operation_error(request, "AmountNet should be less or equal to awarded amount", name="value")
        else:
            if amount > award.value.amount:
                raise_operation_error(request, "Amount should be less or equal to awarded amount", name="value")


def validate_update_contract_value_amount(request, name="value", allow_equal=False):
    data = request.validated["data"]
    contract_value = data.get(name)
    value = data.get("value") or data.get(name)
    if contract_value and requested_fields_changes(request, (name, "status")):
        amount = to_decimal(contract_value.get("amount"))
        amount_net = to_decimal(contract_value.get("amountNet"))
        tax_included = value.get("valueAddedTaxIncluded")

        if not (amount == 0 and amount_net == 0):
            if tax_included:
                amount_max = (amount_net * AMOUNT_NET_COEF).quantize(Decimal("1E-2"), rounding=ROUND_UP)
                if (amount <= amount_net or amount > amount_max) and not allow_equal:
                    raise_operation_error(
                        request,
                        "Amount should be greater than amountNet and differ by "
                        "no more than {}%".format(AMOUNT_NET_COEF * 100 - 100),
                        name=name,
                    )
                elif (amount < amount_net or amount > amount_max) and allow_equal:
                    raise_operation_error(
                        request,
                        "Amount should be equal or greater than amountNet and differ by "
                        "no more than {}%".format(AMOUNT_NET_COEF * 100 - 100),
                        name=name,
                    )
            else:
                if amount != amount_net:
                    raise_operation_error(request, "Amount and amountNet should be equal", name=name)


def validate_contract_signing(request):
    tender = request.validated["tender"]
    data = request.validated["data"]
    if request.context.status != "active" and "status" in data and data["status"] == "active":
        award = [a for a in tender.awards if a.id == request.context.awardID][0]
        stand_still_end = award.complaintPeriod.endDate
        if stand_still_end > get_now():
            raise_operation_error(
                request, "Can't sign contract before stand-still period end ({})".format(stand_still_end.isoformat())
            )
        pending_complaints = [
            i
            for i in tender.complaints
            if i.status in tender.block_complaint_status and i.relatedLot in [None, award.lotID]
        ]
        pending_awards_complaints = [
            i
            for a in tender.awards
            for i in a.complaints
            if i.status in tender.block_complaint_status and a.lotID == award.lotID
        ]
        if pending_complaints or pending_awards_complaints:
            raise_operation_error(request, "Can't sign contract before reviewing all complaints")


def is_positive_float(value):
    if value <= 0:
        raise ValidationError(u"Float value should be greater than 0.")


def validate_ua_road(classification_id, additional_classifications):
    road_count = sum([1 for i in additional_classifications if i["scheme"] == UA_ROAD_SCHEME])
    if is_ua_road_classification(classification_id):
        if road_count > 1:
            raise ValidationError(
                u"Item shouldn't have more than 1 additionalClassification with scheme {}".format(UA_ROAD_SCHEME)
            )
    elif road_count != 0:
        raise ValidationError(
            u"Item shouldn't have additionalClassification with scheme {} "
            u"for cpv not starts with {}".format(UA_ROAD_SCHEME, ", ".join(UA_ROAD_CPV_PREFIXES))
        )


def validate_gmdn(classification_id, additional_classifications):
    gmdn_count = sum([1 for i in additional_classifications if i["scheme"] == GMDN_SCHEME])
    if is_gmdn_classification(classification_id):
        inn_anc_count = sum([1 for i in additional_classifications if i["scheme"] in [INN_SCHEME, ATC_SCHEME]])
        if 0 not in [inn_anc_count, gmdn_count]:
            raise ValidationError(
                u"Item shouldn't have additionalClassifications with both schemes {}/{} and {}".format(
                    INN_SCHEME, ATC_SCHEME, GMDN_SCHEME
                )
            )
        if gmdn_count > 1:
            raise ValidationError(
                u"Item shouldn't have more than 1 additionalClassification with scheme {}".format(GMDN_SCHEME)
            )
    elif gmdn_count != 0:
        raise ValidationError(
            u"Item shouldn't have additionalClassification with scheme {} "
            u"for cpv not starts with {}".format(GMDN_SCHEME, ", ".join(GMDN_CPV_PREFIXES))
        )


def validate_milestones(value):
    if isinstance(value, list):
        sums = defaultdict(Decimal)
        for milestone in value:
            if milestone["type"] == "financing":
                percentage = milestone.get("percentage")
                if percentage:
                    sums[milestone.get("relatedLot")] += to_decimal(percentage)

        for uid, sum_value in sums.items():
            if sum_value != Decimal("100"):
                raise ValidationError(
                    u"Sum of the financial milestone percentages {} is not equal 100{}.".format(
                        sum_value, u" for lot {}".format(uid) if uid else ""
                    )
                )


def validate_procurement_type_of_first_stage(request):
    tender = request.validated["tender"]
    if tender.procurementMethodType not in FIRST_STAGE_PROCUREMENT_TYPES:
        request.errors.add(
            "data",
            "procurementMethodType",
            u"Should be one of the first stage values: {}".format(FIRST_STAGE_PROCUREMENT_TYPES),
        )
        request.errors.status = 422
        raise error_handler(request.errors)


def validate_tender_matches_plan(request):
    plan = request.validated["plan"]
    tender = request.validated["tender"]

    plan_identifier = plan.procuringEntity.identifier
    tender_identifier = tender.procuringEntity.identifier
    if plan_identifier.id != tender_identifier.id or plan_identifier.scheme != tender_identifier.scheme:
        request.errors.add(
            "data",
            "procuringEntity",
            u"procuringEntity.identifier doesn't match: {} {} != {} {}".format(
                plan_identifier.scheme, plan_identifier.id, tender_identifier.scheme, tender_identifier.id
            ),
        )

    pattern = plan.classification.id[:3] if plan.classification.id.startswith("336") else plan.classification.id[:4]
    for i, item in enumerate(tender.items):
        if item.classification.id[: len(pattern)] != pattern:
            request.errors.add(
                "data",
                "items[{}].classification.id".format(i),
                u"Plan classification.id {} and item's {} should be of the same group {}".format(
                    plan.classification.id, item.classification.id, pattern
                ),
            )

    if request.errors:
        request.errors.status = 422
        raise error_handler(request.errors)


def validate_tender_plan_procurement_method_type(request):
    plan = request.validated["plan"]
    tender = request.validated["tender"]

    if plan.tender.procurementMethodType not in (tender.procurementMethodType, "centralizedProcurement"):
        request.errors.add(
            "data",
            "procurementMethodType",
            u"procurementMethodType doesn't match: {} != {}".format(
                plan.tender.procurementMethodType, tender.procurementMethodType
            ),
        )
        request.errors.status = 422
        raise error_handler(request.errors)


def validate_plan_budget_breakdown(request):
    plan = request.validated["plan"]

    if not plan.budget or not plan.budget.breakdown:
        request.errors.add("data", "budget.breakdown", u"Plan should contain budget breakdown")
        request.errors.status = 422
        raise error_handler(request.errors)


def validate_tender_in_draft(request):
    if request.validated["tender"].status != "draft":
        raise raise_operation_error(request, u"Only allowed in draft tender status")


def validate_procurement_kind_is_central(request):
    kind = "central"
    if request.validated["tender"].procuringEntity.kind != kind:
        raise raise_operation_error(request, u"Only allowed for procurementEntity.kind = '{}'".format(kind))


def validate_tender_plan_data(request):
    data = validate_data(request, type(request.tender).plans.model_class)
    plan_id = data["id"]
    update_logging_context(request, {"plan_id": plan_id})

    plan = extract_plan_adapter(request, plan_id)
    with handle_data_exceptions(request):
        plan.validate()
    request.validated["plan"] = plan
    request.validated["plan_src"] = plan.serialize("plain")


def validate_complaint_type_change(request):
    tender = request.validated["tender"]
    if get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19:
        complaint = request.validated["complaint"]
        if complaint.type == "claim":
            raise_operation_error(request, "Can't update claim to complaint")


def validate_update_contract_status_by_supplier(request):
    if request.authenticated_role == "contract_supplier":
        data = request.validated["data"]
        if "status" in data and data["status"] != "pending" or request.context.status != "pending.winner-signing":
            raise_operation_error(request, "Supplier can change status to `pending`")


def validate_role_for_contract_document_operation(request):
    if request.authenticated_role not in ("tender_owner", "contract_supplier",):
        raise_operation_error(request, "Can {} document only buyer or supplier".format(OPERATIONS.get(request.method)))
    if request.authenticated_role == "contract_supplier" and \
            request.validated["contract"].status != "pending.winner-signing":
        raise_operation_error(
            request, "Supplier can't {} document in current contract status".format(OPERATIONS.get(request.method))
        )
    if request.authenticated_role == "tender_owner" and \
            request.validated["contract"].status == "pending.winner-signing":
        raise_operation_error(
            request, "Tender onwer can't {} document in current contract status".format(OPERATIONS.get(request.method))
        )
