from cornice.resource import resource

from openprocurement.api.constants import AgreementType
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.agreement import AgreementsResource
from openprocurement.framework.ifi.procedure.state.agreement import IFIAgreementState


@resource(
    name=f"{AgreementType.INTERNATIONAL_FINANCIAL_INSTITUTIONS}:Agreements",
    collection_path="/agreements",
    path="/agreements/{agreement_id}",
    description=f"{AgreementType.INTERNATIONAL_FINANCIAL_INSTITUTIONS} agreements",
    agreementType=AgreementType.INTERNATIONAL_FINANCIAL_INSTITUTIONS,
    accept="application/json",
)
class IFIAgreementResource(AgreementsResource):
    state_class = IFIAgreementState

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
