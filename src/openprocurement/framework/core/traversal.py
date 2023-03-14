from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.traversal import get_item


class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        # (Allow, Everyone, ALL_PERMISSIONS),
        (Allow, Everyone, "view_listing"),
        (Allow, Everyone, "view_framework"),
        (Allow, Everyone, "view_submission"),
        (Allow, Everyone, "view_agreement"),
        (Allow, "g:brokers", "create_framework"),
        (Allow, "g:chronograph", "edit_framework"),
        (Allow, "g:framework_owner", "edit_framework"),
        (Allow, "g:Administrator", "edit_framework"),
        # Submission permissions
        (Allow, "g:brokers", "create_submission"),
        (Allow, "g:chronograph", "edit_submission"),
        (Allow, "g:submission_owner", "edit_submission"),
        (Allow, "g:Administrator", "edit_submission"),
        # Qualification permissions
        (Allow, Everyone, "view_qualification"),
        (Allow, "g:bots", "create_qualification"),
        (Allow, "g:bots", "edit_qualification"),
        (Allow, "g:framework_owner", "edit_qualification"),
        (Allow, "g:Administrator", "edit_qualification"),
        (Allow, "g:admins", ALL_PERMISSIONS),
        # Agreement permissions
        (Allow, "g:agreements", "create_agreement"),
        (Allow, "g:chronograph", "edit_agreement"),
        (Allow, "g:Administrator", "edit_agreement"),
        (Allow, "g:admins", ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request


def resolve_document(request, obj, document_type=None):
    return get_item(obj, "{}_document".format(document_type) if document_type else "document", request)


def base_factory(request, obj_name):
    obj_name_src = "%s_src" % obj_name
    obj_name_config = "%s_config" % obj_name
    obj_name_id = "%s_id" % obj_name

    request.validated[obj_name_src] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get(obj_name_id):
        return root
    request.validated[obj_name_id] = request.matchdict[obj_name_id]
    obj = getattr(request, obj_name)
    obj.__parent__ = root
    request.validated[obj_name] = request.validated["db_doc"] = obj
    request.validated[obj_name_config] = obj.get("config") or {}
    if request.method != "GET":
        request.validated[obj_name_src] = obj.serialize("plain")
    if request.method != "GET" and obj._initial.get("next_check"):
        request.validated[obj_name_src]["next_check"] = obj._initial.get("next_check")

    request.validated["id"] = request.matchdict[obj_name_id]
    if request.matchdict.get("document_id"):
        return resolve_document(request, obj)

    return obj


def framework_factory(request):
    return base_factory(request, "framework")


def submission_factory(request):
    return base_factory(request, "submission")


def qualification_factory(request):
    return base_factory(request, "qualification")


def agreement_factory(request):
    agreement = base_factory(request, "agreement")
    if request.matchdict.get("contract_id"):
        return get_item(agreement, "contract", request)
    return agreement


def contract_factory(request):
    request.validated["agreement_src"] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get("agreement_id"):
        return root
    request.validated["agreement_id"] = request.matchdict["agreement_id"]
    agreement = request.agreement
    agreement.__parent__ = root
    request.validated["agreement"] = request.validated["db_doc"] = agreement
    request.validated["agreement_config"] = agreement.get("config") or {}
    if request.method != "GET":
        request.validated["agreement_src"] = agreement.serialize("plain")
    if request.matchdict.get("contract_id"):
        return resolve_contract(request, agreement)
    request.validated["id"] = request.matchdict["agreement_id"]
    return agreement


def resolve_contract(request, obj):
    contract = get_item(obj, "contract", request)
    if request.matchdict.get("milestone_id"):
        return resolve_milestone(request, contract,)
    return contract


def resolve_milestone(request, obj):
    milestone = get_item(obj, "milestone", request)
    if request.matchdict.get("document_id"):
        return resolve_document(request, milestone)
    return milestone
