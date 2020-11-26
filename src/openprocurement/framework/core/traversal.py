from pyramid.security import ALL_PERMISSIONS, Allow, Everyone


class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        # (Allow, Everyone, ALL_PERMISSIONS),
        (Allow, Everyone, "view_listing"),
        (Allow, Everyone, "view_framework"),
        (Allow, "g:brokers", "create_framework"),
        (Allow, "g:chronograph", "edit_framework"),
        (Allow, "g:framework_owner", "edit_framework"),
        (Allow, "g:Administrator", "edit_framework"),
        (Allow, "g:admins", ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db


def factory(request):
    request.validated["framework_src"] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get("framework_id"):
        return root
    request.validated["framework_id"] = request.matchdict["framework_id"]
    framework = request.framework
    framework.__parent__ = root
    request.validated["framework"] = request.validated["db_doc"] = framework
    if request.method != "GET":
        request.validated["framework_src"] = framework.serialize("plain")
    if request.method != "GET" and framework._initial.get("next_check"):
        request.validated["framework_src"]["next_check"] = framework._initial.get("next_check")

    request.validated["id"] = request.matchdict["framework_id"]

    return framework
