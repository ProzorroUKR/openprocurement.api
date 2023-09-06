from copy import deepcopy

from pyramid.security import Allow, Everyone, ALL_PERMISSIONS

from openprocurement.api.views.base import BaseResource
from openprocurement.api.utils import get_tender_by_id
from openprocurement.contracting.core.procedure.state.contract import BaseContractState


class ContractBaseResource(BaseResource):

    state_class = BaseContractState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_contract"),
            (Allow, Everyone, "view_listing"),
            (Allow, "g:contracting", "create_contract"),
            (Allow, "g:brokers", "edit_contract"),
            (Allow, "g:Administrator", "edit_contract"),

            (Allow, "g:brokers", "upload_contract_documents"),
            (Allow, "g:brokers", "edit_contract_documents"),

            (Allow, "g:bots", "edit_contract_transactions"),
            (Allow, "g:brokers", "edit_contract_transactions"),

            (Allow, "g:admins", ALL_PERMISSIONS),    # some tests use this, idk why
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)

        self.state = self.state_class(request)

        # https://github.com/Cornices/cornice/issues/479#issuecomment-388407385
        # init is called twice (with and without context), thanks to cornice.

        if not context:

            match_dict = request.matchdict
            if match_dict and match_dict.get("contract_id"):
                request.validated["contract_src"] = request.contract_doc
                contract = request.validated["contract"] = deepcopy(request.validated["contract_src"])
                if "buyer" in contract:
                    request.validated["tender"] = get_tender_by_id(request, contract["tender_id"])
                    self.request.validated["tender_src"] = deepcopy(request.validated["tender"])
