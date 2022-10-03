from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.agreement import TenderAgreementResource
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.tender.cfaselectionua.procedure.models.agreement import Agreement, PatchAgreement
from openprocurement.tender.cfaselectionua.procedure.state.agreement import AgreementState
from pyramid.security import Allow, Everyone
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Agreements",
    collection_path="/tenders/{tender_id}/agreements",
    path="/tenders/{tender_id}/agreements/{agreement_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender EU agreements",
)
class CFASelectionTenderAgreementResource(TenderAgreementResource):
    state_class = AgreementState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:agreement_selection", "edit_agreement_selection"),
        ]
        return acl

    @json_view(
        content_type="application/json",
        permission="edit_agreement_selection",  # brokers
        validators=(
            validate_input_data(PatchAgreement),
            validate_patch_data_simple(Agreement, item_name="agreement"),
        ),
    )
    def patch(self):
        return super().patch()
