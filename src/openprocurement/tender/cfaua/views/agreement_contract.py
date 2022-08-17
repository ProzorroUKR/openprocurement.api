# -*- coding: utf-8 -*-
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.api.views.base import BaseResource
from openprocurement.tender.core.utils import apply_patch, save_tender

from openprocurement.tender.cfaua.validation import (
    validate_agreement_contract_unitprices_update,
    validate_patch_agreement_contract_data,
    validate_agreement_operation_not_in_allowed_status,
)
from openprocurement.tender.cfaua.utils import agreement_resource


# @agreement_resource(
#     name="closeFrameworkAgreementUA:Tender Agreements Contract",
#     collection_path="/tenders/{tender_id}/agreements/{agreement_id}/contracts",
#     path="/tenders/{tender_id}/agreements/{agreement_id}/contracts/{contract_id}",
#     procurementMethodType="closeFrameworkAgreementUA",
#     description="Tender CFAUA agreement contracts",
# )
class TenderAgreementContractResource(BaseResource):
    """ CFA UA Tender Agreement Contract Resource """

    @json_view(permission="view_tender")
    def collection_get(self):
        """ List contracts for Agreement """

        return {"data": [i.serialize() for i in self.request.context.contracts]}

    @json_view(permission="view_tender")
    def get(self):
        """ Retrieving the contract for Agreement """

        return {"data": self.request.validated["contract"].serialize()}

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_agreement_operation_not_in_allowed_status,
            validate_patch_agreement_contract_data,
            validate_agreement_contract_unitprices_update,
        ),
    )
    def patch(self):
        """ Update contract """
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender agreement {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_agreement_contract_patch"}),
            )
            return {"data": self.request.context.serialize()}
