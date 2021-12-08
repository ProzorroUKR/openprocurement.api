from logging import getLogger
from pyramid.security import Allow
from openprocurement.api.utils import get_now, context_unpack

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
    if (
            tender.contracts
            and any([contract.status == "active" for contract in tender.contracts])
            and not any([contract.status == "pending" for contract in tender.contracts])
    ):
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
