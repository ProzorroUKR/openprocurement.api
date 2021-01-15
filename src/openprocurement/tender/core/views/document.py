# -*- coding: utf-8 -*-
from openprocurement.api.views.document import BaseDocumentResource
from openprocurement.tender.core.utils import save_tender, apply_patch


class CoreDocumentResource(BaseDocumentResource):
    container = "documents"
    context_name = "tender"

    def save(self, request, **kwargs):
        return save_tender(request)

    def apply(self, request, **kwargs):
        return apply_patch(request, **kwargs)
