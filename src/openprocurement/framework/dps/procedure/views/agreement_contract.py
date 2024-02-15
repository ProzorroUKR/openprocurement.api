# -*- coding: utf-8 -*-
from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
    validate_patch_data,
)
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.models.contract import (
    Contract,
    PatchContract,
)
from openprocurement.framework.core.procedure.validation import (
    validate_agreement_operation_not_in_allowed_status,
)
from openprocurement.framework.core.procedure.views.contract import (
    AgreementContractsResource,
)
from openprocurement.framework.dps.constants import DPS_TYPE


@resource(
    name=f"{DPS_TYPE}:Agreements Contracts",
    collection_path="/agreements/{agreement_id}/contracts",
    path="/agreements/{agreement_id}/contracts/{contract_id}",
    description=f"{DPS_TYPE} agreements contracts",
    agreementType=DPS_TYPE,
    accept="application/json",
)
class DPSAgreementContractsResource(AgreementContractsResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("framework"),
            validate_input_data(PatchContract),
            validate_patch_data(Contract, item_name="contract"),
            validate_agreement_operation_not_in_allowed_status,
        ),
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
