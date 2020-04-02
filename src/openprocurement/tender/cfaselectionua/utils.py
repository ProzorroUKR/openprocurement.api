# -*- coding: utf-8 -*-
from barbecue import chef
from logging import getLogger
from zope.component import queryUtility
from openprocurement.api.constants import TZ
from openprocurement.api.models import Value
from openprocurement.tender.belowthreshold.utils import add_contract
from openprocurement.tender.cfaselectionua.interfaces import ICFASelectionUAChange
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.cfaselectionua.constants import (
    AGREEMENT_STATUS,
    AGREEMENT_ITEMS,
    AGREEMENT_EXPIRED,
    AGREEMENT_CHANGE,
    AGREEMENT_CONTRACTS,
    AGREEMENT_IDENTIFIER,
    AGREEMENT_START_DATE,
)
from openprocurement.tender.cfaselectionua.traversal import agreement_factory
from openprocurement.tender.core.utils import (
    cleanup_bids_for_cancelled_lots,
    remove_draft_bids,
    calculate_tender_business_date,
    get_first_revision_date,
    CancelTenderLot as BaseCancelTenderLot,
)
from functools import partial
from cornice.resource import resource
from openprocurement.api.utils import error_handler, context_unpack, get_now

LOGGER = getLogger("openprocurement.tender.cfaselectionua")

agreement_resource = partial(resource, error_handler=error_handler, factory=agreement_factory)


class CancelTenderLot(BaseCancelTenderLot):
    def add_next_award_method(request):
        return add_next_award(request)


def get_change_class(instance, data):
    return queryUtility(ICFASelectionUAChange, data["rationaleType"])


def check_bids(request):
    tender = request.validated["tender"]

    if tender.lots:
        [
            setattr(i.auctionPeriod, "startDate", None)
            for i in tender.lots
            if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate
        ]
        [setattr(i, "status", "unsuccessful") for i in tender.lots if i.numberOfBids == 0 and i.status == "active"]
        cleanup_bids_for_cancelled_lots(tender)
        if not set([i.status for i in tender.lots]).difference(set(["unsuccessful", "cancelled"])):
            tender.status = "unsuccessful"
        elif max([i.numberOfBids for i in tender.lots if i.status == "active"]) < 2:
            add_next_award(request)
    else:
        if tender.numberOfBids < 2 and tender.auctionPeriod and tender.auctionPeriod.startDate:
            tender.auctionPeriod.startDate = None
        if tender.numberOfBids == 0:
            tender.status = "unsuccessful"
        if tender.numberOfBids == 1:
            add_next_award(request)


def check_status(request):
    tender = request.validated["tender"]
    now = get_now()
    for award in tender.awards:
        if award.status == "active" and not any([i.awardID == award.id for i in tender.contracts]):
            add_contract(request, award, now)
            add_next_award(request)

    after_enquiryPeriod_endDate = (
        not tender.tenderPeriod.startDate and tender.enquiryPeriod.endDate.astimezone(TZ) <= now
    )
    after_tenderPeriod_startDate = tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.astimezone(TZ) <= now
    if tender.status == "active.enquiries" and (after_enquiryPeriod_endDate or after_tenderPeriod_startDate):
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "active.tendering"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.tendering"}),
        )
        tender.status = "active.tendering"
        return

    elif not tender.lots and tender.status == "active.tendering" and tender.tenderPeriod.endDate <= now:
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], "active.auction"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.auction"}),
        )
        tender.status = "active.auction"
        remove_draft_bids(request)
        check_bids(request)
        if tender.numberOfBids < 2 and tender.auctionPeriod:
            tender.auctionPeriod.startDate = None
        return
    elif tender.lots and tender.status == "active.tendering" and tender.tenderPeriod.endDate <= now:
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], "active.auction"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.auction"}),
        )
        tender.status = "active.auction"
        remove_draft_bids(request)
        check_bids(request)
        [setattr(i.auctionPeriod, "startDate", None) for i in tender.lots if i.numberOfBids < 2 and i.auctionPeriod]
        return


def check_tender_status(request):
    tender = request.validated["tender"]
    now = get_now()
    if tender.lots:
        for lot in tender.lots:
            if lot.status != "active":
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            if not lot_awards:
                continue
            last_award = lot_awards[-1]
            if last_award.status == "unsuccessful":
                LOGGER.info(
                    "Switched lot {} of tender {} to {}".format(lot.id, tender.id, "unsuccessful"),
                    extra=context_unpack(request, {"MESSAGE_ID": "switched_lot_unsuccessful"}, {"LOT_ID": lot.id}),
                )
                lot.status = "unsuccessful"
                continue
            elif last_award.status == "active" and any(
                [i.status == "active" and i.awardID == last_award.id for i in tender.contracts]
            ):
                LOGGER.info(
                    "Switched lot {} of tender {} to {}".format(lot.id, tender.id, "complete"),
                    extra=context_unpack(request, {"MESSAGE_ID": "switched_lot_complete"}, {"LOT_ID": lot.id}),
                )
                lot.status = "complete"
        statuses = set([lot.status for lot in tender.lots])

        if statuses == set(["cancelled"]):
            LOGGER.info(
                "Switched tender {} to {}".format(tender.id, "cancelled"),
                extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_cancelled"}),
            )
            tender.status = "cancelled"
        elif not statuses.difference(set(["unsuccessful", "cancelled"])):
            LOGGER.info(
                "Switched tender {} to {}".format(tender.id, "unsuccessful"),
                extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
            )
            tender.status = "unsuccessful"
        elif not statuses.difference(set(["complete", "unsuccessful", "cancelled"])):
            LOGGER.info(
                "Switched tender {} to {}".format(tender.id, "complete"),
                extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_complete"}),
            )
            tender.status = "complete"
    else:
        last_award_status = tender.awards[-1].status if tender.awards else ""
        if last_award_status == "unsuccessful":
            LOGGER.info(
                "Switched tender {} to {}".format(tender.id, "unsuccessful"),
                extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
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
    if tender.lots:
        statuses = set()
        for lot in tender.lots:
            if lot.status != "active":
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            if lot_awards and lot_awards[-1].status in ["pending", "active"]:
                statuses.add(lot_awards[-1].status if lot_awards else "unsuccessful")
                continue
            lot_items = [i.id for i in tender.items if i.relatedLot == lot.id]
            features = [
                i
                for i in (tender.features or [])
                if i.featureOf == "tenderer"
                or i.featureOf == "lot"
                and i.relatedItem == lot.id
                or i.featureOf == "item"
                and i.relatedItem in lot_items
            ]
            codes = [i.code for i in features]
            bids = [
                {
                    "id": bid.id,
                    "value": [i for i in bid.lotValues if lot.id == i.relatedLot][0].value,
                    "tenderers": bid.tenderers,
                    "parameters": [i for i in bid.parameters if i.code in codes],
                    "date": [i for i in bid.lotValues if lot.id == i.relatedLot][0].date,
                }
                for bid in tender.bids
                if lot.id in [i.relatedLot for i in bid.lotValues]
            ]
            if not bids:
                lot.status = "unsuccessful"
                statuses.add("unsuccessful")
                continue
            unsuccessful_awards = [i.bid_id for i in lot_awards if i.status == "unsuccessful"]
            bids = chef(bids, features, unsuccessful_awards)
            if bids:
                bid = bids[0]
                award = type(tender).awards.model_class(
                    {
                        "bid_id": bid["id"],
                        "lotID": lot.id,
                        "status": "pending",
                        "value": bid["value"],
                        "date": get_now(),
                        "suppliers": bid["tenderers"],
                    }
                )
                tender.awards.append(award)
                request.response.headers["Location"] = request.route_url(
                    "{}:Tender Awards".format(tender.procurementMethodType), tender_id=tender.id, award_id=award["id"]
                )
                statuses.add("pending")
            else:
                statuses.add("unsuccessful")
        if statuses.difference(set(["unsuccessful", "active"])):
            tender.awardPeriod.endDate = None
            tender.status = "active.qualification"
        else:
            tender.awardPeriod.endDate = now
            tender.status = "active.awarded"
    else:
        if not tender.awards or tender.awards[-1].status not in ["pending", "active"]:
            unsuccessful_awards = [i.bid_id for i in tender.awards if i.status == "unsuccessful"]
            bids = chef(tender.bids, tender.features or [], unsuccessful_awards)
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
                tender.awards.append(award)
                request.response.headers["Location"] = request.route_url(
                    "{}:Tender Awards".format(tender.procurementMethodType), tender_id=tender.id, award_id=award["id"]
                )
        if tender.awards[-1].status == "pending":
            tender.awardPeriod.endDate = None
            tender.status = "active.qualification"
        else:
            tender.awardPeriod.endDate = now
            tender.status = "active.awarded"


def prepare_shortlistedFirms(shortlistedFirms):
    """ Make list with keys
        key = {identifier_id}_{identifier_scheme}_{lot_id}
    """
    shortlistedFirms = shortlistedFirms if shortlistedFirms else []
    all_keys = set()
    for firm in shortlistedFirms:
        key = u"{firm_id}_{firm_scheme}".format(
            firm_id=firm["identifier"]["id"], firm_scheme=firm["identifier"]["scheme"]
        )
        # if firm.get('lots'):
        # keys = set([u"{key}_{lot_id}".format(key=key, lot_id=lot['id']) for lot in firm.get('lots')])
        # else:
        # keys = set([key])
        keys = set([key])
        all_keys |= keys
    return all_keys


def prepare_bid_identifier(bid):
    """ Make list with keys
        key = {identifier_id}_{identifier_scheme}_{lot_id}
    """
    all_keys = set()
    for tenderer in bid["tenderers"]:
        key = u"{id}_{scheme}".format(id=tenderer["identifier"]["id"], scheme=tenderer["identifier"]["scheme"])
        # if bid.get('lotValues'):
        # keys = set([u"{key}_{lot_id}".format(key=key,
        # lot_id=lot['relatedLot'])
        # for lot in bid.get('lotValues')])
        # else:
        # keys = set([key])
        keys = set([key])
        all_keys |= keys
    return all_keys


def calculate_item_identification_tuple(item):
    additionalClassifications = ()
    if item.additionalClassifications:
        additionalClassifications = tuple(
            (additionalClassifications.id, additionalClassifications.scheme)
            for additionalClassifications in item.additionalClassifications
        )
    if item.unit:
        code = item.unit.code
    else:
        code = None
    return (item.id, item.classification.id, item.classification.scheme, code, additionalClassifications)


def check_agreement_status(request, tender):
    if tender.agreements[0].status != "active":
        drop_draft_to_unsuccessful(request, tender, AGREEMENT_STATUS)


def check_period_and_items(request, tender):
    agreement_items = tender.agreements[0].items if tender.agreements[0].items else []
    agreement_items_ids = {calculate_item_identification_tuple(agreement_item) for agreement_item in agreement_items}
    tender_items_ids = {calculate_item_identification_tuple(tender_item) for tender_item in tender.items}

    if not tender_items_ids.issubset(agreement_items_ids):
        drop_draft_to_unsuccessful(request, tender, AGREEMENT_ITEMS)
        return

    delta = -request.content_configurator.agreement_expired_until
    date = calculate_tender_business_date(tender.agreements[0].period.endDate, delta, tender)
    if get_now() > date:
        drop_draft_to_unsuccessful(request, tender, AGREEMENT_EXPIRED)
    elif tender.agreements[0].period.startDate > tender.date:
        drop_draft_to_unsuccessful(request, tender, AGREEMENT_START_DATE)


def check_pending_changes(request, tender):
    changes = tender.agreements[0].changes if tender.agreements[0].changes else None
    if changes:
        for change in changes:
            if change.status == "pending":
                drop_draft_to_unsuccessful(request, tender, AGREEMENT_CHANGE)
                return


def check_min_active_contracts(request, tender):
    for agr in tender.agreements:
        active_contracts = [c for c in agr.contracts if c.status == "active"] if agr.contracts else []
        if len(active_contracts) < request.content_configurator.min_active_contracts:
            drop_draft_to_unsuccessful(request, tender, AGREEMENT_CONTRACTS)


def check_agreement(request, tender):
    tender.unsuccessfulReason = []
    check_agreement_status(request, tender)
    check_period_and_items(request, tender)
    check_pending_changes(request, tender)
    check_min_active_contracts(request, tender)
    check_identifier(request, tender)


def calculate_agreement_contracts_value_amount(request, tender):
    agreement = tender.agreements[0]
    tender_items = dict((i.id, i.quantity) for i in tender.items)
    for contract in agreement.contracts:
        value = Value()
        value.amount = 0
        value.currency = contract.unitPrices[0].value.currency
        value.valueAddedTaxIncluded = contract.unitPrices[0].value.valueAddedTaxIncluded
        for unitPrice in contract.unitPrices:
            if unitPrice.relatedItem in tender_items:
                value.amount += unitPrice.value.amount * tender_items[unitPrice.relatedItem]
        value.amount = round(value.amount, 2)
        contract.value = value
    tender.lots[0].value = max([contract.value for contract in agreement.contracts], key=lambda value: value.amount)
    tender.value = tender.lots[0].value


def calculate_tender_features(request, tender):
    #  calculation tender features after items validation
    if tender.agreements[0].features:
        tender_features = []
        tender_items_ids = {i.id for i in tender.items}
        for feature in tender.agreements[0].features:
            if feature.featureOf == "tenderer":
                tender_features.append(feature)
            elif feature.featureOf == "item" and feature.relatedItem in tender_items_ids:
                tender_features.append(feature)
            elif feature.featureOf == "lot" and feature.relatedItem == tender.lots[0].id:
                tender_features.append(feature)

        tender.features = tender_features


def check_identifier(request, tender):
    if tender.agreements[0].procuringEntity:
        if (
            tender.procuringEntity.identifier.id != tender.agreements[0].procuringEntity.identifier.id
            or tender.procuringEntity.identifier.scheme != tender.agreements[0].procuringEntity.identifier.scheme
        ):
            drop_draft_to_unsuccessful(request, tender, AGREEMENT_IDENTIFIER)


def drop_draft_to_unsuccessful(request, tender, cause):
    LOGGER.info(
        "Switched tender {} to {}".format(tender.id, "draft.unsuccessful"),
        extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_draft.unsuccessful"}, {"CAUSE": cause}),
    )
    tender.status = "draft.unsuccessful"
    tender.unsuccessfulReason.append(cause)
