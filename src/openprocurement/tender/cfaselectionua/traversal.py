# -*- coding: utf-8 -*-
from openprocurement.tender.core.traversal import Root, get_item


def agreement_factory(request):
    request.validated["tender_src"] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get("tender_id"):
        return root
    request.validated["tender_id"] = request.matchdict["tender_id"]
    tender = request.tender
    tender.__parent__ = root
    request.validated["tender"] = request.validated["db_doc"] = tender
    request.validated["tender_status"] = tender.status
    if request.method != "GET":
        request.validated["tender_src"] = tender.serialize("plain")
    if request.matchdict.get("agreement_id"):
        agreement = get_item(tender, "agreement", request)
        if request.matchdict.get("change_id"):
            change = get_item(agreement, "change", request)
            return change
        elif request.matchdict.get("document_id"):
            return get_item(agreement, "document", request)
        elif request.matchdict.get("contract_id"):
            return get_item(agreement, "contract", request)
        else:
            return agreement
    request.validated["id"] = request.matchdict["tender_id"]
    return tender
