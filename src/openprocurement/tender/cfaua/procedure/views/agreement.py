from openprocurement.api.utils import json_view
from openprocurement.tender.cfaua.procedure.serializers.agreement import AgreementSerializer
from openprocurement.tender.core.procedure.validation import (
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.tender.core.procedure.views.agreement import TenderAgreementResource
from openprocurement.tender.cfaua.procedure.state.agreement import AgreementState
from openprocurement.tender.cfaua.procedure.models.agreement import Agreement, PatchAgreement
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Agreements",
    collection_path="/tenders/{tender_id}/agreements",
    path="/tenders/{tender_id}/agreements/{agreement_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU agreements",
)
class CFAUAAgreementResource(TenderAgreementResource):
    serializer_class = AgreementSerializer
    state_class = AgreementState

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PatchAgreement),
            validate_patch_data_simple(Agreement, item_name="agreement"),
        ),
    )
    def patch(self):
        return super().patch()
