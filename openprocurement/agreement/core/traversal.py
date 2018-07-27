# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.component import queryUtility
from openprocurement.api.traversal import get_item
from openprocurement.agreement.core.interfaces import IContextFactory
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


@implementer(IContextFactory)
class BaseCFAContextFactory(object):

    def __init__(self, root):
        self.root = root

    def __call__(self, request):
        request.validated['agreement_src'] = {}
        root = self.root(request)
        if not request.matchdict or not request.matchdict.get('agreement_id'):
            return root
        request.validated['agreement_id'] = request.matchdict['agreement_id']
        agreement = request.agreement
        agreement.__parent__ = root
        request.validated['agreement'] = request.validated['db_doc'] = agreement
        if request.method != 'GET':
            request.validated['agreement_src'] = agreement.serialize('plain')
        request.validated['id'] = request.matchdict['agreement_id']
        return agreement


def factory(request):
    configurator = request.content_configurator
    context_factory = queryUtility(
        IContextFactory,
        name=configurator.agreement_type,
        default=cfaContextFactory,
        )
    return context_factory(request)


cfaContextFactory = BaseCFAContextFactory(Root)