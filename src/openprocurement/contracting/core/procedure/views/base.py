from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.utils import (
    get_tender_by_id,
    request_init_contract,
    request_init_tender,
)
from openprocurement.api.views.base import BaseResource
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
            (Allow, "g:admins", ALL_PERMISSIONS),  # some tests use this, idk why
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
                contract_doc = request.contract_doc
                request_init_contract(request, contract_doc)

                if "buyer" in contract_doc and request.method not in ("GET", "HEAD"):
                    tender_doc = get_tender_by_id(request, contract_doc["tender_id"])
                    request_init_tender(request, tender_doc)
                    award = [
                        award
                        for award in tender_doc.get("awards", [])
                        if award.get("id") == contract_doc.get("awardID")
                    ][0]
                    request.validated["award"] = award
