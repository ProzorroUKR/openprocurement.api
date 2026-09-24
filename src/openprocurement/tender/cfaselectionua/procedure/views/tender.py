from copy import deepcopy

from cornice.resource import resource
from pyramid.security import Allow

from openprocurement.api.context import set_request_now
from openprocurement.api.procedure.validation import (
    validate_request_by_state,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.cfaselectionua.procedure.state.tender_details import (
    CFASelectionTenderDetailsState,
)
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.views.tender import TendersResource


@resource(
    name="closeFrameworkAgreementSelectionUA:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="closeFrameworkAgreementSelectionUA tenders",
    accept="application/json",
)
class CFASelectionTenderResource(TendersResource):
    state_class = CFASelectionTenderDetailsState

    def __acl__(self):
        acl = super().__acl__()
        acl.append(
            (Allow, "g:agreement_selection", "edit_tender"),
        )
        return acl

    @json_view(
        content_type="application/json",
        validators=(validate_request_by_state,),
        permission="edit_tender",
    )
    def patch(self):
        result = deepcopy(super().patch())

        # imitate bridge behavior
        # TODO: remove this with draft.pending removal
        tender = self.request.validated["tender"]
        if tender["status"] == "draft.pending":
            set_request_now()
            self.request.authenticated_role = "agreement_selection"
            tender_src = self.request.validated["tender_src"] = deepcopy(tender)
            agreement = self.state.copy_agreement_data(tender)
            if agreement:
                tender["status"] = "active.enquiries"
            else:
                tender["status"] = "draft.unsuccessful"
            self.state.validate_tender_patch(tender_src, tender)
            self.state.on_patch(tender_src, tender)
            if save_tender(self.request):
                self.LOGGER.info(
                    f"Updated tender {tender['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"}),
                )

        return result
