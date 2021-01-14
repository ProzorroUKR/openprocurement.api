# -*- coding: utf-8 -*-
from openprocurement.agreement.core.utils import save_agreement, apply_patch
from openprocurement.api.views.document import BaseDocumentResource


class CoreDocumentResource(BaseDocumentResource):
    container = "documents"
    context_name = "agreement"

    def save(self, request, **kwargs):
        return save_agreement(request)

    def apply(self, request, **kwargs):
        return apply_patch(request, **kwargs)
