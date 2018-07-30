# -*- coding: utf-8 -*-
from zope.interface import implementer
from openprocurement.api.traversal import get_item
from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Everyone,
    )


class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, Everyone, 'view_listing'),
        (Allow, Everyone, 'view_agreement'),
        (Allow, 'g:agreements', 'create_agreement'),
        (Allow, 'g:Administrator', 'edit_agreement'),
        (Allow, 'g:admins', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db


def factory(request):
    request.validated['agreement_src'] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get('agreement_id'):
        return root
    request.validated['agreement_id'] = request.matchdict['agreement_id']
    agreement = request.agreement
    agreement.__parent__ = root
    request.validated['agreement'] = request.validated['db_doc'] = agreement
    if request.method != 'GET':
        request.validated['agreement_src'] = agreement.serialize('plain')
    if request.matchdict.get('document_id'):
        return get_item(agreement, 'document', request)
    if request.matchdict.get('contract_id'):
        return get_item(agreement, 'contract', request)
    request.validated['id'] = request.matchdict['agreement_id']
    return agreement