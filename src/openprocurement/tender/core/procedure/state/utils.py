

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
