# -*- coding: utf-8 -*-
from openprocurement.api.traversal import get_item
from openprocurement.framework.core.traversal import resolve_document, Root


def contract_factory(request):
    request.validated["agreement_src"] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get("agreement_id"):
        return root
    request.validated["agreement_id"] = request.matchdict["agreement_id"]
    agreement = request.agreement
    agreement.__parent__ = root
    request.validated["agreement"] = request.validated["db_doc"] = agreement
    if request.method != "GET":
        request.validated["agreement_src"] = agreement.serialize("plain")
    if request.matchdict.get("contract_id"):
        return resolve_contract(request, agreement)
    request.validated["id"] = request.matchdict["agreement_id"]
    return agreement


def resolve_contract(request, obj):
    contract = get_item(obj, "contract", request)
    if request.matchdict.get("milestone_id"):
        return resolve_milestone(request, contract,)
    return contract


def resolve_milestone(request, obj):
    milestone = get_item(obj, "milestone", request)
    if request.matchdict.get("document_id"):
        return resolve_document(request, milestone)
    return milestone
