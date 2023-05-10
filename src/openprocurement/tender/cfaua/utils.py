# -*- coding: utf-8 -*-
from logging import getLogger
from functools import partial

from cornice.resource import resource
from openprocurement.api.utils import error_handler, context_unpack, get_now
from openprocurement.tender.core.utils import (
    calculate_tender_business_date,
)
from openprocurement.tender.cfaua.traversal import (
    agreement_factory,
    qualifications_factory,
    bid_financial_documents_factory,
    bid_eligibility_documents_factory,
    bid_qualification_documents_factory,
)
from openprocurement.tender.cfaua.constants import (
    MIN_BIDS_NUMBER,
    CLARIFICATIONS_UNTIL_PERIOD,
)


LOGGER = getLogger(__name__)


agreement_resource = partial(resource, error_handler=error_handler, factory=agreement_factory)
qualifications_resource = partial(resource, error_handler=error_handler, factory=qualifications_factory)
bid_financial_documents_resource = partial(
    resource, error_handler=error_handler, factory=bid_financial_documents_factory
)
bid_eligibility_documents_resource = partial(
    resource, error_handler=error_handler, factory=bid_eligibility_documents_factory
)
bid_qualification_documents_resource = partial(
    resource, error_handler=error_handler, factory=bid_qualification_documents_factory
)


def check_tender_status_on_active_qualification_stand_still(request):

    tender = request.validated["tender"]
    now = get_now()
    active_lots = [
        lot.id for lot in tender.lots
        if lot.status == "active"
    ] if tender.lots else [None]

    if not (
        tender.awardPeriod
        and tender.awardPeriod.endDate <= now
        and not any(
            [
                i.status in tender.block_complaint_status
                for a in tender.awards
                for i in a.complaints
                if a.lotID in active_lots
            ]
        )
    ):
        return
    statuses = set()
    if tender.lots:
        for lot in tender.lots:
            if lot.status != "active":  # pragma: no cover
                statuses.add(lot.status)
                continue
            active_lot_awards = [i for i in tender.awards if i.lotID == lot.id and i.status == "active"]
            if len(active_lot_awards) < MIN_BIDS_NUMBER:
                LOGGER.info(
                    "Switched lot {} of tender {} to {}".format(lot.id, tender.id, "unsuccessful"),
                    extra=context_unpack(request, {"MESSAGE_ID": "switched_lot_unsuccessful"}, {"LOT_ID": lot.id}),
                )
                lot.status = "unsuccessful"
                statuses.add(lot.status)
                continue
            statuses.add(lot.status)
    else:  # pragma: no cover
        active_awards = [i for i in tender.awards if i.status == "active"]
        if len(active_awards) <= MIN_BIDS_NUMBER:
            statuses.add("unsuccessful")
        else:
            statuses.add("active.awarded")

    if statuses == {"cancelled"}:  # pragma: no cover
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "cancelled"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_cancelled"}),
        )
        tender.status = "cancelled"
    elif not statuses.difference({"unsuccessful", "cancelled"}):  # pragma: no cover
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "unsuccessful"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
        )
        tender.status = "unsuccessful"
    else:
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "active.awarded"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active_awarded"}),
        )
        tender.status = "active.awarded"
        clarif_date = calculate_tender_business_date(now, CLARIFICATIONS_UNTIL_PERIOD, tender, False)
        tender.contractPeriod = {
            "startDate": now,
            "clarificationsUntil": clarif_date
        }
        lots = [l for l in tender.get("lots", []) if l.status == "active"]
        if lots:
            for lot in lots:
                agreement_data = generate_agreement_data(request, tender, lot)
                agreement = type(tender).agreements.model_class(agreement_data)
                agreement.__parent__ = tender
                tender.agreements.append(agreement)
        else:  # pragma: no cover
            agreement_data = generate_agreement_data(request, tender)
            agreement = type(tender).agreements.model_class(agreement_data)
            agreement.__parent__ = tender
            tender.agreements.append(agreement)

        # Update tender status (awarded, unsuccessful)


def generate_agreement_data(request, tender, lot=None):
    data = {
        "items": tender.items if not lot else [i for i in tender.items if i.relatedLot == lot.id],
        "agreementID": "{}-{}{}".format(tender.tenderID, request.registry.server_id, len(tender.agreements) + 1),
        "date": get_now().isoformat(),
        "contracts": [],
        "features": tender.features,
    }
    unit_prices = [
        {
            "relatedItem": item.id,
            "value": {"currency": tender.value.currency, "valueAddedTaxIncluded": tender.value.valueAddedTaxIncluded},
        }
        for item in data["items"]
    ]
    for award in tender.awards:
        if lot and lot.id != award.lotID:
            continue
        if award.status != "active":
            continue
        data["contracts"].append(
            {
                "suppliers": award.suppliers,
                "awardID": award.id,
                "bidID": award.bid_id,
                "date": get_now().isoformat(),
                "unitPrices": unit_prices,
                "parameters": [b for b in tender.bids if b.id == award.bid_id][0].parameters,
            }
        )
    return data
