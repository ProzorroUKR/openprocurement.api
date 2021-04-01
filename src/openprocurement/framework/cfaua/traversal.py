# -*- coding: utf-8 -*-
from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.traversal import get_item


class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, Everyone, "view_listing"),
        (Allow, Everyone, "view_agreement"),
        (Allow, "g:contracting", "create_agreement"),
        (Allow, "g:Administrator", "edit_agreement"),
        (Allow, "g:admins", ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request


def change_factory(request):
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
    if request.matchdict.get("document_id"):
        return get_item(agreement, "document", request)
    if request.matchdict.get("change_id"):
        return get_item(agreement, "change", request)
    request.validated["id"] = request.matchdict["agreement_id"]
    return agreement
