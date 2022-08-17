from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.core.procedure.validation import (
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.views.agreement import resolve_agreement
from openprocurement.tender.core.procedure.utils import (
    get_items,
    save_tender,
    set_item,
)
from openprocurement.tender.core.procedure.serializers.base import BaseSerializer
from openprocurement.tender.cfaua.procedure.state.agreement_contract import AgreementContractState
from openprocurement.tender.cfaua.procedure.models.agreement_contract import AgreementContract, PatchAgreementContract
from cornice.resource import resource


def resolve_agreement_contract(request):
    match_dict = request.matchdict
    if match_dict.get("contract_id"):
        contract_id = match_dict["contract_id"]
        contracts = get_items(request, request.validated["agreement"], "contracts", contract_id)
        request.validated["contract"] = contracts[0]


@resource(
    name="closeFrameworkAgreementUA:Tender Agreements Contract",
    collection_path="/tenders/{tender_id}/agreements/{agreement_id}/contracts",
    path="/tenders/{tender_id}/agreements/{agreement_id}/contracts/{contract_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender CFAUA agreement contracts",
)
class CFAUAAgreementContractResource(TenderBaseResource):
    state_class = AgreementContractState
    serializer_class = BaseSerializer

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_agreement(request)
            resolve_agreement_contract(request)

    @json_view(
        permission="view_tender",
    )
    def collection_get(self):
        tender = self.request.validated["agreement"]
        data = [self.serializer_class(b).data for b in tender.get("contracts", "")]
        return {"data": data}

    @json_view(
        permission="view_tender",
    )
    def get(self):
        data = self.serializer_class(self.request.validated["contract"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PatchAgreementContract),
            validate_patch_data_simple(AgreementContract, item_name="contract"),
        ),
    )
    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            contract = self.request.validated["contract"]
            self.state.validate_agreement_contract_on_patch(contract, updated)
            set_item(self.request.validated["agreement"], "contracts", contract["id"], updated)

            self.state.agreement_contract_on_patch(contract, updated)
            self.state.always(self.request.validated["tender"])
            if save_tender(self.request):
                self.LOGGER.info(
                    "Updated tender agreement contract {}".format(contract["id"]),
                    extra=context_unpack(self.request,
                                         {"MESSAGE_ID": "tender_agreement_contract_patch"}),
                )
                return {"data": self.serializer_class(updated).data}
