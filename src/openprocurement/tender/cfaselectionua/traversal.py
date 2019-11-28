# -*- coding: utf-8 -*-
from openprocurement.tender.core.traversal import get_item, handle_root


def agreement_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
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
