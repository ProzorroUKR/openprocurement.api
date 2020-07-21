# -*- coding: utf-8 -*-
from openprocurement.api.utils import\
    json_view, raise_operation_error, context_unpack, get_now
from openprocurement.tender.core.utils import optendersresource,\
    apply_patch, save_tender
from openprocurement.tender.core.validation import (
    validate_patch_contract_data,
    validate_update_contract_value,
    validate_contract_operation_not_in_allowed_status,
    validate_update_contract_value_with_award,
    validate_update_contract_value_amount,
    validate_update_contract_value_net_required,
    validate_update_contract_status_by_supplier
)
from openprocurement.tender.belowthreshold.views.contract\
    import TenderAwardContractResource
from openprocurement.tender.pricequotation.constants import PMT
from openprocurement.tender.pricequotation.utils import check_tender_status


@optendersresource(
    name="{}:Tender Contracts".format(PMT),
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType=PMT,
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class PQTenderAwardContractResource(TenderAwardContractResource):
    """"""
    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            validate_patch_contract_data,
            validate_contract_operation_not_in_allowed_status,
            validate_update_contract_status_by_supplier,
            validate_update_contract_value,
            validate_update_contract_value_net_required,
            validate_update_contract_value_with_award,
            validate_update_contract_value_amount,
        ),
    )
    def patch(self):
        """Update of contract
        """
        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if contract_status != self.request.context.status and \
                (contract_status not in ("pending", "pending.winner-signing",) or \
                self.request.context.status not in ("active", "pending", "pending.winner-signing",)):
            raise_operation_error(self.request, "Can't update contract status")
        if self.request.context.status == "active" and not self.request.context.dateSigned:
            self.request.context.dateSigned = get_now()
        check_tender_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender contract {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_contract_patch"}),
            )
            return {"data": self.request.context.serialize()}
