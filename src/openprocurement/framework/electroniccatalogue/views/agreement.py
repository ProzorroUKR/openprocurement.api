from openprocurement.api.utils import APIResource, json_view, context_unpack
from openprocurement.framework.core.utils import agreementsresource, apply_patch
from openprocurement.framework.electroniccatalogue.utils import check_contract_statuses, check_agreement_status


@agreementsresource(
    name="electronicCatalogue:Agreements",
    path="/agreements/{agreement_id}",
    agreementType="electronicCatalogue",
    description="Agreements resource"
)
class AgreementResource(APIResource):
    @json_view(permission="view_agreement")
    def get(self):
        return {"data": self.context.serialize("view")}

    @json_view(permission="edit_agreement")
    def patch(self):
        if self.request.authenticated_role == "chronograph":
            check_agreement_status(self.request)
            check_contract_statuses(self.request)
        if apply_patch(self.request, obj_name="agreement", src=self.request.validated["agreement_src"]):
            self.LOGGER.info(f"Updated agreement {self.request.validated['agreement'].id}",
                             extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"}))
        return {"data": self.request.context.serialize("view")}
