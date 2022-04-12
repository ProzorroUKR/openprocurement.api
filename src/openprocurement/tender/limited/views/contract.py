# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, get_now
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import (
    validate_contract_data,
    validate_patch_contract_data,
    validate_update_contract_value,
    validate_update_contract_value_with_award,
    validate_update_contract_value_amount,
    validate_update_contract_value_net_required,
    validate_activate_contract,
)
from openprocurement.tender.belowthreshold.views.contract import (
    TenderAwardContractResource as BaseTenderAwardContractResource,
)
from openprocurement.tender.limited.utils import (
    check_tender_status,
    check_tender_negotiation_status,
)
from openprocurement.tender.limited.validation import (
    validate_contract_update_in_cancelled,
    validate_contract_operation_not_in_active,
    validate_contract_items_count_modification,
    validate_contract_with_cancellations_and_contract_signing,
    validate_update_contract_status,
)


# @optendersresource(
#     name="reporting:Tender Contracts",
#     collection_path="/tenders/{tender_id}/contracts",
#     procurementMethodType="reporting",
#     path="/tenders/{tender_id}/contracts/{contract_id}",
#     description="Tender contracts",
# )
class TenderAwardContractResource(BaseTenderAwardContractResource):
    @staticmethod
    def check_tender_status_method(request):
        return check_tender_status(request)

    @json_view(
        content_type="application/json",
        permission="create_contract",
        validators=(
            validate_contract_data,
            validate_contract_operation_not_in_active
        ),
    )
    def collection_post(self):
        return super(TenderAwardContractResource, self).collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_patch_contract_data,
            validate_contract_operation_not_in_active,
            validate_contract_update_in_cancelled,
            validate_update_contract_status,
            validate_update_contract_value,
            validate_update_contract_value_net_required,
            validate_update_contract_value_with_award,
            validate_update_contract_value_amount,
            validate_contract_items_count_modification,
        ),
    )
    def patch(self):
        """
        Update of contract
        """
        self.request.context.date = get_now()
        return super(TenderAwardContractResource, self).patch()


# @optendersresource(
#     name="negotiation:Tender Contracts",
#     collection_path="/tenders/{tender_id}/contracts",
#     procurementMethodType="negotiation",
#     path="/tenders/{tender_id}/contracts/{contract_id}",
#     description="Tender contracts",
# )
class TenderNegotiationAwardContractResource(TenderAwardContractResource):
    """
    Tender Negotiation Award Contract Resource
    """
    @staticmethod
    def check_tender_status_method(request):
        return check_tender_negotiation_status(request)

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_patch_contract_data,
            validate_contract_operation_not_in_active,
            validate_contract_update_in_cancelled,
            validate_contract_with_cancellations_and_contract_signing,
            validate_update_contract_status,
            validate_update_contract_value,
            validate_update_contract_value_net_required,
            validate_update_contract_value_with_award,
            validate_update_contract_value_amount,
            validate_contract_items_count_modification,
        ),
    )
    def patch(self):
        """
        Update of contract
        """
        self.request.context.date = get_now()
        return super(TenderNegotiationAwardContractResource, self).patch()


# @optendersresource(
#     name="negotiation.quick:Tender Contracts",
#     collection_path="/tenders/{tender_id}/contracts",
#     procurementMethodType="negotiation.quick",
#     path="/tenders/{tender_id}/contracts/{contract_id}",
#     description="Tender contracts",
# )
class TenderNegotiationQuickAwardContractResource(TenderNegotiationAwardContractResource):
    """
    Tender Negotiation Quick Award Contract Resource
    """
