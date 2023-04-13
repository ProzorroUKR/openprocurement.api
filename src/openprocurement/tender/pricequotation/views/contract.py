# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import (
    validate_patch_contract_data,
    validate_update_contract_value,
    validate_contract_operation_not_in_allowed_status,
    validate_update_contract_value_with_award,
    validate_update_contract_value_amount,
    validate_update_contract_value_net_required,
    validate_update_contract_status_by_supplier,
    validate_activate_contract,
    validate_update_contract_status,
)
from openprocurement.tender.belowthreshold.views.contract import (
    TenderAwardContractResource,
)
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.utils import check_tender_status


# @optendersresource(
#     name="{}:Tender Contracts".format(PMT),
#     collection_path="/tenders/{tender_id}/contracts",
#     procurementMethodType=PMT,
#     path="/tenders/{tender_id}/contracts/{contract_id}",
#     description="Tender contracts",
# )
class PQTenderAwardContractResource(TenderAwardContractResource):
    @staticmethod
    def check_tender_status_method(request):
        return check_tender_status(request)

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            validate_patch_contract_data,
            validate_contract_operation_not_in_allowed_status,
            validate_update_contract_status_by_supplier,
            validate_update_contract_status,
            validate_update_contract_value,
            validate_update_contract_value_net_required,
            validate_update_contract_value_with_award,
            validate_update_contract_value_amount,
        ),
    )
    def patch(self):
        """
        Update of contract
        """
        return super(PQTenderAwardContractResource, self).patch()
