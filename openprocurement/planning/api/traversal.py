# -*- coding: utf-8 -*-
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
        (Allow, Everyone, 'view_plan'),
        (Allow, 'g:brokers', 'create_plan'),
        (Allow, 'g:Administrator', 'edit_plan'),
        (Allow, 'g:Administrator', 'revision_plan'),
        (Allow, 'g:admins', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db


def factory(request):
    request.validated['plan_src'] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get('plan_id'):
        return root
    request.validated['plan_id'] = request.matchdict['plan_id']
    plan = request.plan
    plan.__parent__ = root
    request.validated['plan'] = request.validated['db_doc'] = plan
    if request.method != 'GET':
        request.validated['plan_src'] = plan.serialize('plain')
    if request.matchdict.get('document_id'):
        return get_item(plan, 'document', request)
    request.validated['id'] = request.matchdict['plan_id']
    return plan
