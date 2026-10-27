from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.document import (
    CoreMilestoneDocumentResource,
)
from openprocurement.framework.ifi.constants import IFI_TYPE


@resource(
    name=f"{IFI_TYPE}:Agreements Contracts Milestone Documents",
    collection_path="/agreements/{agreement_id}/contracts/{contract_id}/milestones/{milestone_id}/documents",
    path="/agreements/{agreement_id}/contracts/{contract_id}/milestones/{milestone_id}/documents/{document_id}",
    description="Agreement contract milestone related binary files (PDFs, etc.)",
    agreementType=IFI_TYPE,
)
class MilestoneDocumentResource(CoreMilestoneDocumentResource):
    @json_view(
        permission="view_framework",
    )
    def collection_get(self):
        return super().collection_get()

    @json_view(
        permission="view_framework",
    )
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
