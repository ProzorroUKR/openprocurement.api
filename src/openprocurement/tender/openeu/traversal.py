# -*- coding: utf-8 -*-
from openprocurement.tender.core.traversal import (
    get_item, handle_root, resolve_complaint, resolve_document,
    resolve_bid, resolve_milestone, resolve_requirement_response,
)


def qualifications_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
    if request.matchdict.get("qualification_id"):
        return resolve_qualification(request, tender)
    request.validated["id"] = request.matchdict["tender_id"]
    return tender


def resolve_qualification(request, obj):
    qualification = get_item(obj, "qualification", request)
    if request.matchdict.get("complaint_id"):
        return resolve_complaint(request, qualification)
    elif request.matchdict.get("milestone_id"):
        return resolve_milestone(request, qualification)
    elif request.matchdict.get("document_id"):
        return resolve_document(request, qualification)
    elif request.matchdict.get("requirement_response_id"):
        return resolve_requirement_response(request, qualification)
    else:
        return qualification


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
