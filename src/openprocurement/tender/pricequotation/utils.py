# -*- coding: utf-8 -*-
from types import NoneType
from operator import itemgetter

from barbecue import chef
from logging import getLogger
from openprocurement.api.constants import TZ, RELEASE_2020_04_19
from openprocurement.api.utils import get_now, context_unpack
from openprocurement.tender.core.utils import (
    calculate_tender_business_date,
    cleanup_bids_for_cancelled_lots,
    remove_draft_bids,
    cancel_tender
)

from openprocurement.tender.core.constants import COMPLAINT_STAND_STILL_TIME
from openprocurement.tender.core.utils import get_first_revision_date
from openprocurement.tender.pricequotation.interfaces import IRequirementResponse
from zope.component import queryUtility


LOGGER = getLogger("openprocurement.tender.pricequotation")


def check_bids(request):
    tender = request.validated["tender"]
    new_rules = get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19

    if new_rules and any([i.status not in ["active", "unsuccessful"] for i in tender.cancellations]):
        return
    if tender.numberOfBids == 0:
        tender.status = "unsuccessful"
    else:
        # tender.status = 'active.qualification'
        add_next_award(request)


def add_contract(request, award, now=None):
    tender = request.validated["tender"]
    tender.contracts.append(
        type(tender).contracts.model_class(
            {
                "awardID": award.id,
                "suppliers": award.suppliers,
                "value": generate_contract_value(tender, award),
                "date": now or get_now(),
                "items": [i for i in tender.items if not hasattr(award, "lotID") or i.relatedLot == award.lotID],
                "contractID": "{}-{}{}".format(tender.tenderID, request.registry.server_id, len(tender.contracts) + 1),
            }
        )
    )


def generate_contract_value(tender, award):
    if award.value:
        value = type(tender).contracts.model_class.value.model_class(dict(award.value.items()))
        value.amountNet = award.value.amount
        return value
    return None


def check_cancellation_status(request, cancel_tender_method=cancel_tender):
    tender = request.validated["tender"]
    cancellations = tender.cancellations

    for cancellation in cancellations:
        if cancellation.status == "pending":
            cancellation.status = "active"
            if cancellation.cancellationOf == "tender":
                cancel_tender_method(request)


def check_status(request):
    tender = request.validated["tender"]
    now = get_now()
    check_cancellation_status(request)

    for award in tender.awards:
        if award.status == "active" and not any([i.awardID == award.id for i in tender.contracts]):
            add_contract(request, award, now)
            add_next_award(request)
    if tender.status == "active.tendering" and tender.tenderPeriod.endDate <= now:
        tender.status = "active.qualification"
        remove_draft_bids(request)
        check_bids(request)
        status = tender.status
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], status),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_{}".format(status)}),
        )
        return
    elif tender.status == "active.awarded":
        check_tender_status(request)


def check_tender_status(request):
    tender = request.validated["tender"]
    last_award_status = tender.awards[-1].status if tender.awards else ""
    if last_award_status == "unsuccessful":
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "unsuccessful"),
            extra=context_unpack(
                request,
                {"MESSAGE_ID": "switched_tender_unsuccessful"}
            ),
        )
        tender.status = "unsuccessful"
    if tender.contracts and tender.contracts[-1].status == "active":
        tender.status = "complete"


def add_next_award(request):
    tender = request.validated["tender"]
    now = get_now()
    if not tender.awardPeriod:
        tender.awardPeriod = type(tender).awardPeriod({})
    if not tender.awardPeriod.startDate:
        tender.awardPeriod.startDate = now
    if not tender.awards or tender.awards[-1].status not in ["pending", "active"]:
        unsuccessful_awards = [
            a.bid_id for a in tender.awards
            if a.status == "unsuccessful"
        ]
        bids = tender.bids
        if bids:
            bid = bids[0].serialize()
            award = type(tender).awards.model_class(
                {
                    "bid_id": bid["id"],
                    "status": "pending",
                    "date": get_now(),
                    "value": bid["value"],
                    "suppliers": bid["tenderers"],
                }
            )
            award.__parent__ = tender
            tender.awards.append(award)
            request.response.headers["Location"] = request.route_url(
                "{}:Tender Awards".format(tender.procurementMethodType),
                tender_id=tender.id,
                award_id=award["id"]
            )
    if tender.awards[-1].status == "pending":
        tender.awardPeriod.endDate = None
        tender.status = "active.qualification"
    else:
        tender.awardPeriod.endDate = now
        tender.status = "active.awarded"


def reformat_response(resp):
    return [
        {
            'id': r['requirement']['id'],
            'response': r['id'],
            'value': r['value']
        }
        for r in resp
    ]


def reformat_criteria(criterias):
    return [
        {
            'id': req['id'],
            'dataType': req['dataType'],
            'maxValue': req.get("maxValue"),
            'minValue': req.get("minValue"),
            'expectedValue': req.get("expectedValue"),
        }
        for criteria in criterias
        for req_group in criteria['requirementGroups']
        for req in req_group['requirements']
    ]


def sort_by_id(group):
    return sorted(group, key=itemgetter('id'))
