from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.core.procedure.views.document import BaseDocumentResource


class BaseAwardDocumentResource(BaseDocumentResource, TenderAwardResource):
    item_name = "award"

    def __init__(self, request, context=None):
        TenderAwardResource.__init__(self, request, context)
        BaseDocumentResource.__init__(self, request, context)

    def set_doc_author(self, doc):
        doc["author"] = self.request.authenticated_role
        return doc

    @json_view(permission="view_tender")
    def collection_get(self):
        return super(BaseAwardDocumentResource, self).collection_get()

    @json_view(permission="view_tender")
    def get(self):
        return super(BaseAwardDocumentResource, self).get()
