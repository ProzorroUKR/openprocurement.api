from openprocurement.tender.core.procedure.context import get_now
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.api.constants import TZ, RELEASE_2020_04_19


def cancellation_blocks_tender(tender):
    if get_first_revision_date(tender, default=get_now()) < RELEASE_2020_04_19:
        return False

    if tender["procurementMethodType"] not in ("belowThreshold", "closeFrameworkAgreementSelectionUA"):
        return False

    if any(i["status"] == "pending" for i in tender.get("cancellations", "")):
        return True

    accept_tender = all(
        any(complaint["status"] == "resolved" for complaint in c.get("complaints"))
        for c in tender.get("cancellations", "")
        if c["status"] == "unsuccessful" and c.get("complaints")
    )
    return not accept_tender


def has_unanswered_questions(tender, filter_cancelled_lots=True):
    if filter_cancelled_lots and tender.get("lots"):
        active_lots = [l["id"] for l in tender["lots"] if l["status"] == "active"]
        active_items = [i["id"] for i in tender.get("items")
                        if not i.get("relatedLot") or i["relatedLot"] in active_lots]
        return any(
            not i["answer"]
            for i in tender.get("questions", "")
            if i["questionOf"] == "tender"
            or i["questionOf"] == "lot" and i["relatedItem"] in active_lots
            or i["questionOf"] == "item" and i["relatedItem"] in active_items
        )
    return any(not i["answer"] for i in tender.get("questions", ""))


def has_unanswered_complaints(tender, filter_cancelled_lots=True, block_tender_complaint_status=("pending",)):
    if filter_cancelled_lots and tender.get("lots"):
        active_lots = [l["id"] for l in tender.get("lots") if l["status"] == "active"]
        return any(
            [
                i["status"] in block_tender_complaint_status
                for i in tender.get("complaints", "")
                if not i["relatedLot"] or (i["relatedLot"] in active_lots)
            ])
