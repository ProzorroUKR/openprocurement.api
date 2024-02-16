from pyramid.security import Allow, Everyone

from openprocurement.api.utils import request_init_tender
from openprocurement.historical.core.utils import Root as BaseRoot


class Root(BaseRoot):
    __acl__ = BaseRoot.__acl__ + [
        (Allow, Everyone, "view_tender"),
        (Allow, "g:brokers", "view_historical"),
        (Allow, "g:Administrator", "view_historical"),
    ]


def historical_tender_factory(request):
    root = Root(request)
    if not request.matchdict or not request.matchdict.get("doc_id"):
        return root
    request.validated["tender_id"] = request.matchdict["doc_id"]
    doc = request.extract_doc_versioned("Tender")
    request_init_tender(request, doc)
    request.validated["id"] = request.matchdict["doc_id"]
    request.validated["tender_status"] = doc["status"]

    # making this shitty module work
    root.doc_type = "Tender"
    root.id = doc["_id"]
    root.rev = doc["_rev"]
    return root
