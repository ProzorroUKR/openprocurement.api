# -*- coding: utf-8 -*-

from pyramid.security import ALL_PERMISSIONS, Allow, Deny, Everyone


class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        # (Allow, Everyone, ALL_PERMISSIONS),
        (Allow, "g:admins", ALL_PERMISSIONS),
        (Allow, "g:bots", "upload_tender_documents"),
        (Allow, "g:bots", "search_complaints"),
    ]

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db


def get_item(parent, key, request):
    if "document" in key and key != "document":
        item_type = "document"
        item_field = key.split("_")
        item_field = item_field[0] + item_field[1].capitalize() + "s"
    else:
        item_type = key
        item_field = "{}s".format(item_type)

    item_id_key = "{}_id".format(item_type)
    item_id = request.matchdict[item_id_key]

    request.validated[item_id_key] = item_id
    items = [i for i in getattr(parent, item_field, []) if i.id == item_id]

    if not items:
        from openprocurement.api.utils import error_handler
        request.errors.add("url", item_id_key, "Not Found")
        request.errors.status = 404
        raise error_handler(request.errors)

    if item_type == "document":
        request.validated["{}s".format(item_type)] = items

    item = items[-1]
    request.validated[item_type] = item
    request.validated["id"] = item_id
    item.__parent__ = parent
    return item


def factory(request):
    root = Root(request)
    return root
