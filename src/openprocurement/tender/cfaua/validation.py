# -*- coding: utf-8 -*-
from datetime import datetime
from iso8601 import parse_date
from isodate import duration_isoformat
from schematics.exceptions import ValidationError
from zope.component import getAdapter
from decimal import Decimal

from openprocurement.api.utils import get_now, raise_operation_error, update_logging_context
from openprocurement.api.validation import validate_data, OPERATIONS
from openprocurement.api.interfaces import IContentConfigurator

from openprocurement.tender.cfaua.constants import MIN_BIDS_NUMBER, MAX_AGREEMENT_PERIOD
from openprocurement.tender.core.validation import validate_award_document_tender_not_in_allowed_status_base


def validate_patch_qualification_data(request):
    qualification_class = type(request.context)
    return validate_data(request, qualification_class, True)


# bids
def validate_view_bids_in_active_tendering(request):
    if request.validated["tender_status"] == "active.tendering":
        raise_operation_error(
            request,
            "Can't view {} in current ({}) tender status".format(
                "bid" if request.matchdict.get("bid_id") else "bids", request.validated["tender_status"]
            ),
        )


# bid document
def validate_add_bid_document_not_in_allowed_tender_status(request):
    tender_status = request.validated["tender_status"]
    if tender_status not in ("active.tendering", "active.qualification", "active.qualification.stand-still"):
        raise_operation_error(request, "Can't upload document in current ({}) tender status".format(tender_status))


def validate_add_bid_financial_document_not_in_allowed_tender_status(request):
    tender_status = request.validated["tender_status"]
    if tender_status not in ("active.tendering", "active.qualification",
                             "active.awarded", "active.qualification.stand-still"):
        raise_operation_error(request, "Can't upload document in current ({}) tender status".format(tender_status))


# qualification
def validate_qualification_document_operation_not_in_allowed_status(request):
    if request.validated["tender_status"] != "active.pre-qualification":
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_qualification_document_operation_not_in_pending(request):
    qualification = request.validated["qualification"]
    if qualification.status != "pending":
        raise_operation_error(
            request, "Can't {} document in current qualification status".format(OPERATIONS.get(request.method))
        )


# qualification complaint
def validate_qualification_update_not_in_pre_qualification(request):
    tender = request.validated["tender"]
    if tender.status not in ["active.pre-qualification"]:
        raise_operation_error(request, "Can't update qualification in current ({}) tender status".format(tender.status))


def validate_cancelled_qualification_update(request):
    if request.context.status == "cancelled":
        raise_operation_error(request, "Can't update qualification in current cancelled qualification status")


def validate_add_complaint_not_in_pre_qualification(request):
    tender = request.validated["tender"]
    if tender.status not in ["active.pre-qualification.stand-still"]:
        raise_operation_error(request, "Can't add complaint in current ({}) tender status".format(tender.status))


def validate_update_complaint_not_in_pre_qualification(request):
    tender = request.validated["tender"]
    if tender.status not in ["active.pre-qualification", "active.pre-qualification.stand-still"]:
        raise_operation_error(request, "Can't update complaint in current ({}) tender status".format(tender.status))


def validate_update_qualification_complaint_only_for_active_lots(request):
    tender = request.validated["tender"]
    if any([i.status != "active" for i in tender.lots if i.id == request.validated["qualification"].lotID]):
        raise_operation_error(request, "Can update complaint only in active lot status")


def validate_add_complaint_not_in_qualification_period(request):
    tender = request.validated["tender"]
    if tender.qualificationPeriod and (
        tender.qualificationPeriod.startDate
        and tender.qualificationPeriod.startDate > get_now()
        or tender.qualificationPeriod.endDate
        and tender.qualificationPeriod.endDate < get_now()
    ):
        raise_operation_error(request, "Can add complaint only in qualificationPeriod")


def validate_tender_status_update(request):
    tender = request.context
    data = request.validated["data"]
    if request.authenticated_role == "tender_owner" and "status" in data:
        if tender.status == "active.pre-qualification" and data["status"] not in [
            "active.pre-qualification.stand-still",
            tender.status,
        ]:
            raise_operation_error(request, "Can't update tender status")
        elif tender.status == "active.qualification" and data["status"] not in [
            "active.qualification.stand-still",
            tender.status,
        ]:
            raise_operation_error(request, "Can't update tender status")
        elif data["status"] not in [
            "active.pre-qualification.stand-still",
            "active.qualification.stand-still",
            tender.status,
        ]:
            raise_operation_error(request, "Can't update tender status")


# agreement
def validate_agreement_data(request):
    update_logging_context(request, {"agreement_id": "__new__"})
    model = type(request.tender).agreements.model_class
    return validate_data(request, model)


def validate_patch_agreement_data(request):
    model = type(request.tender).agreements.model_class
    return validate_data(request, model, True)


def validate_agreement_operation_not_in_allowed_status(request):
    if request.validated["tender_status"] != "active.awarded":
        raise_operation_error(
            request,
            "Can't {} agreement in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_update_agreement_only_for_active_lots(request):
    tender = request.validated["tender"]
    awards_id = request.context.get_awards_id()
    if any(
        [i.status != "active" for i in tender.lots if i.id in [a.lotID for a in tender.awards if a.id in awards_id]]
    ):
        raise_operation_error(request, "Can update agreement only in active lot status")


def validate_agreement_signing(request):
    tender = request.validated["tender"]
    data = request.validated["data"]
    config = getAdapter(tender, IContentConfigurator)
    if request.context.status != "active" and "status" in data and data["status"] == "active":
        if "period" not in data or not data["period"]:
            raise_operation_error(request, "Period is required for agreement signing.")
        if not data["period"]["startDate"] or not data["period"]["endDate"]:
            raise_operation_error(request, "startDate and endDate are required in agreement.period.")
        agreement_start_date = parse_date(data["period"]["startDate"])
        agreement_end_date = parse_date(data["period"]["endDate"])
        calculated_end_date = agreement_start_date + config.max_agreement_period
        if calculated_end_date < agreement_end_date:
            raise_operation_error(
                request,
                "Agreement period can't be greater than {}.".format(duration_isoformat(config.max_agreement_period)),
            )
        awards = [a for a in tender.awards if a.id in request.context.get_awards_id()]
        lots_id = set([a.lotID for a in awards] + [None])
        pending_complaints = [
            i for i in tender.complaints if i.status in tender.block_complaint_status and i.relatedLot in lots_id
        ]
        pending_awards_complaints = [
            i
            for a in tender.awards
            for i in a.complaints
            if i.status in tender.block_complaint_status and a.lotID in lots_id
        ]
        if pending_complaints or pending_awards_complaints:
            raise_operation_error(request, "Can't sign agreement before reviewing all complaints")
        empty_unitprices = []
        active_contracts = []
        for contract in request.context.contracts:
            if contract.status == "active":
                active_contracts.append(contract.id)
                for unit_price in contract.unitPrices:
                    empty_unitprices.append(unit_price.value.amount is None)
        if any(empty_unitprices):
            raise_operation_error(request, "Can't sign agreement without all contracts.unitPrices.value.amount")
        if len(active_contracts) < config.min_bids_number:
            raise_operation_error(request, "Agreement don't reach minimum active contracts.")


def validate_agreement_update_with_accepted_complaint(request):
    tender = request.validated["tender"]
    awards_id = request.context.get_awards_id()
    if any(
        [
            any([c.status == "accepted" for c in i.complaints])
            for i in tender.awards
            if i.lotID in [a.lotID for a in tender.awards if a.id in awards_id]
        ]
    ):
        raise_operation_error(request, "Can't update agreement with accepted complaint")


# award complaint
def validate_add_complaint_not_in_qualification_stand_still(request):
    tender = request.validated["tender"]
    if tender.status not in ("active.qualification.stand-still",):
        raise_operation_error(
            request,
            "Can't {} complaint in current ({}) tender status".format(OPERATIONS.get(request.method), tender.status),
        )


def validate_update_complaint_not_in_qualification(request):
    tender = request.validated["tender"]
    if tender.status not in ("active.qualification", "active.qualification.stand-still"):
        raise_operation_error(
            request,
            "Can't {} complaint in current ({}) tender status".format(OPERATIONS.get(request.method), tender.status),
        )


def validate_add_complaint_not_in_complaint_period(request):
    if not request.context.complaintPeriod or (
        request.context.complaintPeriod
        and (
            request.context.complaintPeriod.startDate
            and request.context.complaintPeriod.startDate > get_now()
            or request.context.complaintPeriod.endDate
            and request.context.complaintPeriod.endDate < get_now()
        )
    ):
        raise_operation_error(request, "Can add complaint only in complaintPeriod")


def validate_max_awards_number(number, *args):
    if number < MIN_BIDS_NUMBER:
        raise ValidationError("Maximal awards number can't be less then minimal bids number")


# agreement contract
def validate_patch_agreement_contract_data(request):
    model = type(request.tender).agreements.model_class.contracts.model_class
    return validate_data(request, model, True)


def validate_agreement_contract_unitprices_update(request):
    contract = request.context
    tender = request.validated["tender"]
    agreement_items_id = {u.relatedItem for u in contract.unitPrices}
    validated_items_id = {
        u["relatedItem"] for u in request.validated["data"]["unitPrices"] if u["value"]["amount"] is not None
    }
    quantity_cache = {i.id: Decimal(str(i.quantity)) for i in contract.__parent__.items}
    if request.validated["data"]["status"] == "active" or "unitPrices" in request.validated["json_data"]:
        if len(agreement_items_id) != len(validated_items_id):
            raise_operation_error(request, "unitPrice.value.amount count doesn't match with contract.")
        elif agreement_items_id != validated_items_id:
            raise_operation_error(request, "All relatedItem values doesn't match with contract.")

        unit_price_amounts = []
        for unit_price in request.validated["data"]["unitPrices"]:
            if unit_price.get("value", {}).get("currency") != tender.value.currency:
                raise_operation_error(request, "currency of bid should be identical to currency of value of lot")
            if unit_price.get("value", {}).get("valueAddedTaxIncluded") != tender.value.valueAddedTaxIncluded:
                raise_operation_error(
                    request, "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot"
                )
            unit_price_amounts.append(quantity_cache[unit_price["relatedItem"]] * unit_price["value"]["amount"])

        calculated_value = sum(unit_price_amounts)

        bid = [b for b in tender.bids if b.id == contract.bidID][0]
        award = [a for a in tender.awards if a.id == contract.awardID][0]
        if award.lotID:
            value = [v for v in bid.lotValues if v.relatedLot == award.lotID][0].value.amount
            error_message = "bid.lotValue.value.amount"
        else:
            value = bid.value.amount
            error_message = "bid.value.amount"

        if calculated_value > value:
            raise_operation_error(request, "Total amount can't be greater than {}".format(error_message))


def validate_max_agreement_duration_period(value):
    date = datetime(1, 1, 1)
    if (date + value) > (date + MAX_AGREEMENT_PERIOD):
        raise ValidationError(
            "Agreement duration period is greater than {}".format(duration_isoformat(MAX_AGREEMENT_PERIOD))
        )


# awards
def validate_update_award_in_not_allowed_status(request):
    tender = request.validated["tender"]
    if tender.status not in ["active.qualification", "active.qualification.stand-still"]:
        raise_operation_error(request, "Can't update award in current ({}) tender status".format(tender.status))


def validate_award_document_tender_not_in_allowed_status(request):
    validate_award_document_tender_not_in_allowed_status_base(
        request, allowed_bot_statuses=("active.awarded", "active.qualification.stand-still")
    )
