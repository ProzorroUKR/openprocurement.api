# -*- coding: utf-8 -*-
from openprocurement.tender.core.traversal import Root, get_item, handle_root, resolve_bid, resolve_document
from openprocurement.tender.openeu.traversal import resolve_qualification


def qualifications_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
    if request.matchdict.get("qualification_id"):
        return resolve_qualification(request, tender)
    request.validated["id"] = request.matchdict["tender_id"]
    return tender


def agreement_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
    if request.matchdict.get("agreement_id"):
        return resolve_agreement(request, tender)
    request.validated["id"] = request.matchdict["tender_id"]
    return tender


def resolve_agreement(request, obj):
    agreement = get_item(obj, "agreement", request)
    if request.matchdict.get("change_id"):
        return resolve_change(agreement, request)
    elif request.matchdict.get("document_id"):
        return resolve_document(request, agreement)
    elif request.matchdict.get("contract_id"):
        return resolve_contract(agreement, request)
    else:
        return agreement


def resolve_contract(agreement, request):
    return get_item(agreement, "contract", request)


def resolve_change(agreement, request):
    return get_item(agreement, "change", request)


def bid_financial_documents_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
    if request.matchdict.get("bid_id"):
        return resolve_bid(request, tender, document_type="financial")


def bid_eligibility_documents_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
    if request.matchdict.get("bid_id"):
        return resolve_bid(request, tender, document_type="eligibility")


def bid_qualification_documents_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
    if request.matchdict.get("bid_id"):
        return resolve_bid(request, tender, document_type="qualification")
