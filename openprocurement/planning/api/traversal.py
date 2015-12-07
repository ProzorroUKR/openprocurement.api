# -*- coding: utf-8 -*-

from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Everyone,
)


class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, Everyone, 'view_plan'),
        (Allow, 'g:brokers', 'create_plan'),
        (Allow, 'g:brokers', 'edit_plan'),
        (Allow, 'g:Administrator', 'edit_plan'),
        (Allow, 'g:admins', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db


def get_item(parent, key, request, root):
    request.validated['{}_id'.format(key)] = request.matchdict['{}_id'.format(key)]
    items = [i for i in getattr(parent, '{}s'.format(key), []) if i.id == request.matchdict['{}_id'.format(key)]]
    if not items:
        from openprocurement.planning.api.utils import error_handler
        request.errors.add('url', '{}_id'.format(key), 'Not Found')
        request.errors.status = 404
        raise error_handler(request.errors)
    else:
        if key == 'document':
            request.validated['{}s'.format(key)] = items
        item = items[-1]
        request.validated[key] = item
        request.validated['id'] = request.matchdict['{}_id'.format(key)]
        item.__parent__ = parent
        return item


def factory(request):
    request.validated['plan_src'] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get('plan_id'):
        return root
    request.validated['plan_id'] = request.matchdict['plan_id']
    plan = request.plan
    plan.__parent__ = root
    request.validated['plan'] = plan
    if request.method != 'GET':
        request.validated['plan_src'] = plan.serialize('plain')

    request.validated['id'] = request.matchdict['plan_id']
    return plan
