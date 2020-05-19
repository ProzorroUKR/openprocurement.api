# -*- coding: utf-8 -*-

from pyramid.security import ALL_PERMISSIONS, Allow, Deny, Everyone
from openprocurement.api.traversal import get_item


class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        # (Allow, Everyone, ALL_PERMISSIONS),
        (Allow, Everyone, "view_listing"),
        (Allow, Everyone, "view_tender"),
        (Allow, "g:brokers", "create_bid"),
        (Allow, "g:brokers", "create_complaint"),
        (Allow, "g:brokers", "create_question"),
        (Allow, "g:brokers", "create_tender"),
        (Allow, "g:auction", "auction"),
        (Allow, "g:auction", "upload_tender_documents"),
        (Allow, "g:contracting", "extract_credentials"),
        (Allow, "g:competitive_dialogue", "create_tender"),
        (Allow, "g:chronograph", "edit_tender"),
        (Allow, "g:Administrator", "edit_tender"),
        (Allow, "g:Administrator", "edit_bid"),
        (Allow, "g:Administrator", "edit_complaint"),
        (Allow, "g:admins", ALL_PERMISSIONS),
        (Allow, "g:bots", "upload_tender_documents"),
        (Allow, "g:bots", "edit_tender"),
        (Allow, "g:bots", "upload_qualification_documents"),
        (Allow, "g:template_registry_bots", "upload_tender_documents"),
        (Allow, "g:renderer_bots", "upload_tender_documents"),
        (Allow, "g:renderer_bots", "upload_contract_documents"),
    ]

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db


def handle_root(request):
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


def factory(request):
    response = handle_root(request)

    if response:
        return response

    tender = request.validated["tender"]

    if request.method != "GET" and tender._initial.get("next_check"):
        request.validated["tender_src"]["next_check"] = tender._initial.get("next_check")

    if request.matchdict.get("award_id"):
        return resolve_award(request, tender)
    elif request.matchdict.get("contract_id"):
        return resolve_contract(request, tender)
    elif request.matchdict.get("bid_id"):
        return resolve_bid(request, tender)
    elif request.matchdict.get("cancellation_id"):
        return resolve_cancellation(request, tender)
    elif request.matchdict.get("complaint_id"):
        return resolve_complaint(request, tender)
    elif request.matchdict.get("document_id"):
        return resolve_document(request, tender)
    elif request.matchdict.get("question_id"):
        return resolve_question(request, tender)
    elif request.matchdict.get("lot_id"):
        return resolve_lot(request, tender)
    elif request.matchdict.get("criterion_id"):
        return resolve_criteria(request, tender)

    request.validated["id"] = request.matchdict["tender_id"]

    return tender


def resolve_complaint(request, obj):
    complaint = get_item(obj, "complaint", request)
    if request.matchdict.get("post_id"):
        return resolve_post(request, complaint)
    elif request.matchdict.get("document_id"):
        return resolve_document(request, complaint)
    else:
        return complaint


def resolve_post(request, obj):
    post = get_item(obj, "post", request)
    if request.matchdict.get("document_id"):
        return resolve_document(request, post)
    else:
        return post


def resolve_cancellation(request, obj):
    cancellation = get_item(obj, "cancellation", request)
    if request.matchdict.get("complaint_id"):
        return resolve_complaint(request, cancellation)
    elif request.matchdict.get("document_id"):
        return resolve_document(request, cancellation)
    else:
        return cancellation


def resolve_bid(request, obj, document_type=None):
    bid = get_item(obj, "bid", request)
    if request.matchdict.get("document_id"):
        return resolve_document(request, bid, document_type=document_type)
    if request.matchdict.get("requirement_response_id"):
        return resolve_requirement_response(request, bid)
    return bid


def resolve_contract(request, obj):
    contract = get_item(obj, "contract", request)
    if request.matchdict.get("document_id"):
        return resolve_document(request, contract)
    else:
        return contract


def resolve_award(request, obj):
    award = get_item(obj, "award", request)
    if request.matchdict.get("complaint_id"):
        return resolve_complaint(request, award)
    elif request.matchdict.get("document_id"):
        return resolve_document(request, award)
    elif request.matchdict.get("milestone_id"):
        return resolve_milestone(request, award)
    elif request.matchdict.get("requirement_response_id"):
        return resolve_requirement_response(request, award)
    else:
        return award


def resolve_lot(request, obj):
    return get_item(obj, "lot", request)


def resolve_question(request, obj):
    return get_item(obj, "question", request)


def resolve_document(request, obj, document_type=None):
    return get_item(obj, "{}_document".format(document_type) if document_type else "document", request)


def resolve_milestone(request, obj):
    return get_item(obj, "milestone", request)


def resolve_requirement(request, obj):
    requirement = get_item(obj, "requirement", request)
    if request.matchdict.get("evidence_id"):
        return get_item(requirement, "evidence", request, where_search="eligibleEvidences")
    return requirement


def resolve_requirement_group(request, obj):
    requirement_group = get_item(obj, "requirement_group", request, "requirementGroups")
    if request.matchdict.get("requirement_id"):
        return resolve_requirement(request, requirement_group)
    return requirement_group


def resolve_criteria(request, obj):
    criteria = get_item(obj, "criterion", request, "criteria")

    if request.matchdict.get("requirement_group_id"):
        return resolve_requirement_group(request, criteria)
    else:
        return criteria


def resolve_requirement_response(request, obj):
    requirement_response = get_item(obj, "requirement_response", request, "requirementResponses")

    if request.matchdict.get("evidence_id"):
        return get_item(requirement_response, "evidence", request)
    return requirement_response
