# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.models import Value
from openprocurement.tender.belowthreshold.utils import (
    add_next_award,
    contracts_allow_to_complete,
)
from openprocurement.tender.cfaselectionua.constants import (
    AGREEMENT_STATUS,
    AGREEMENT_ITEMS,
    AGREEMENT_EXPIRED,
    AGREEMENT_CHANGE,
    AGREEMENT_CONTRACTS,
    AGREEMENT_IDENTIFIER,
    AGREEMENT_START_DATE,
)
from openprocurement.tender.core.utils import (
    calculate_tender_date,
    CancelTenderLot as BaseCancelTenderLot,
)
from openprocurement.api.utils import context_unpack, get_now

LOGGER = getLogger("openprocurement.tender.cfaselectionua")


class CancelTenderLot(BaseCancelTenderLot):

    @staticmethod
    def add_next_award_method(request):
        return add_next_award(request)


def check_bids(request):
    tender = request.validated["tender"]

    if tender.lots:
        [
            setattr(i.auctionPeriod, "startDate", None)
            for i in tender.lots
            if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate
        ]
        [setattr(i, "status", "unsuccessful") for i in tender.lots if i.numberOfBids == 0 and i.status == "active"]
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
            elif last_award.status == "active":
                contracts = [
                    contract for contract in tender.contracts
                    if contract.awardID == last_award.id
                ]
                allow_complete_lot = contracts_allow_to_complete(contracts)
                if allow_complete_lot:
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

        if (
                tender.contracts
                and any([contract.status == "active" for contract in tender.contracts])
                and not any([contract.status == "pending" for contract in tender.contracts])
        ):
            tender.status = "complete"


def prepare_shortlistedFirms(shortlistedFirms):
    """ Make list with keys
        key = {identifier_id}_{identifier_scheme}_{lot_id}
    """
    shortlistedFirms = shortlistedFirms if shortlistedFirms else []
    all_keys = set()
    for firm in shortlistedFirms:
        key = "{firm_id}_{firm_scheme}".format(
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
        key = "{id}_{scheme}".format(id=tenderer["identifier"]["id"], scheme=tenderer["identifier"]["scheme"])
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
    date = calculate_tender_date(tender.agreements[0].period.endDate, delta, tender)
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
