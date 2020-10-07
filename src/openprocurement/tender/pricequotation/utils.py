# -*- coding: utf-8 -*-
from collections import defaultdict
from logging import getLogger
from pyramid.security import Allow
from openprocurement.api.utils import get_now, context_unpack
from openprocurement.tender.core.utils import (
    remove_draft_bids,
    calculate_tender_business_date,
)

from openprocurement.tender.belowthreshold.utils import add_contract
from openprocurement.tender.pricequotation.constants import QUALIFICATION_DURATION


LOGGER = getLogger("openprocurement.tender.pricequotation")


def check_bids(request):
    tender = request.validated["tender"]
    pending_cancellations = [
        i.status not in ["active", "unsuccessful"]
        for i in tender.cancellations
    ]
    if any(pending_cancellations):
        return
    if tender.numberOfBids == 0:
        tender.status = "unsuccessful"
    else:
        add_next_award(request)


def cancel_tender(request):
    tender = request.validated["tender"]
    if tender.status in ["active.tendering"]:
        tender.bids = []
    tender.status = "cancelled"


def check_award_status(request):
    tender = request.validated["tender"]
    now = get_now()
    awards = tender.awards
    is_cancelled = [award for award in tender.awards if award.status == 'cancelled']
    for award in awards:
        if (award.status == 'pending' and
                calculate_tender_business_date(award.date, QUALIFICATION_DURATION, tender) <= now):
            award.status = 'unsuccessful'
            if is_cancelled:
                tender.status = 'unsuccessful'
                LOGGER.info(
                    "Switched tender {} to {}".format(tender["id"], tender.status),
                    extra=context_unpack(request,
                                         {"MESSAGE_ID": "switched_tender_{}".format(tender.status)}),
                )
            else:
                add_next_award(request)
        if award.status == "active" and not any([i.awardID == award.id for i in tender.contracts]):
            add_contract(request, award, now)
            add_next_award(request)


def check_status(request):

    check_award_status(request)

    tender = request.validated["tender"]
    now = get_now()

    if tender.status == "active.tendering" and tender.tenderPeriod.endDate <= now:
        tender.status = "active.qualification"
        remove_draft_bids(request)
        check_bids(request)
        status = tender.status
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], status),
            extra=context_unpack(request,
                                 {"MESSAGE_ID": "switched_tender_{}".format(status)}),
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
        bids = sorted([
            bid for bid in tender.bids
            if bid.id not in unsuccessful_awards
        ], key=lambda bid: bid.value.amount)
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
        else:
            tender.status = 'unsuccessful'
            return
    if tender.awards[-1].status == "pending":
        tender.awardPeriod.endDate = None
        tender.status = "active.qualification"
    else:
        tender.awardPeriod.endDate = now
        tender.status = "active.awarded"


def get_bid_owned_award_acl(award):
    acl = []
    if not hasattr(award, "__parent__") or 'bids' not in award.__parent__:
        return acl
    tender = award.__parent__
    awarded_bid = [bid for bid in tender.bids if bid.id == award.bid_id][0]
    prev_awards = [
        a for a in tender.awards
        if a.bid_id == awarded_bid.id and
        a.id != award.id and
        a['status'] != 'pending'
    ]
    bid_acl = "_".join((awarded_bid.owner, awarded_bid.owner_token))
    owner_acl = "_".join((tender.owner, tender.owner_token))

    if prev_awards or award.status != 'pending':
        acl.extend([
            (Allow, owner_acl, "upload_award_documents"),
            (Allow, owner_acl, "edit_award")
        ])
    else:
        acl.extend([
            (Allow, bid_acl, "upload_award_documents"),
            (Allow, bid_acl, "edit_award")
        ])
    return acl


def find_parent(id_):
    parts = id_.split('-')
    return '-'.join(parts[:-1])


def requirements_to_tree(requirements):
    return {
        requirement['id']: requirement
        for requirement in requirements
    }


def group_to_tree(groups):
    return {
        group['id']: requirements_to_tree(group['requirements'])
        for group in groups
    }


def criteria_to_tree(criterias):
    return {
        criteria['id']: group_to_tree(criteria['requirementGroups'])
        for criteria in criterias
    }


def responses_to_tree(responses):
    groups = defaultdict(dict)
    for response in responses:
        groups[find_parent(response.requirement.id)][response['requirement']['id']] = response

    criterias = defaultdict(dict)
    for group_id, group in groups.items():
        criterias[find_parent(group_id)][group_id] = group
    return criterias
