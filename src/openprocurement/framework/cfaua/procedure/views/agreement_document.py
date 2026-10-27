from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.framework.cfaua.procedure.state.document import (
    AgreementDocumentState,
)
from openprocurement.framework.cfaua.procedure.views.base import AgreementBaseResource
from openprocurement.framework.core.procedure.views.base import BaseDocumentResource
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


@resource(
    name=f"{CFA_UA}:Agreement Documents",
    collection_path="/agreements/{agreement_id}/documents",
    path="/agreements/{agreement_id}/documents/{document_id}",
    agreementType=CFA_UA,
    description="Agreement Documents",
)
class AgreementDocumentsResource(AgreementBaseResource, BaseDocumentResource):
    item_name = "agreement"
    serializer_class = DocumentSerializer
    state_class = AgreementDocumentState

    @json_view(permission="view_agreement")
    def collection_get(self):
        return super().collection_get()

    @json_view(permission="view_agreement")
    def get(self):
        return super().get()

    @json_view(
        permission="edit_agreement",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        permission="edit_agreement",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
