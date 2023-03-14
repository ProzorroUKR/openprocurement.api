from openprocurement.api.utils import json_view
from openprocurement.api.views.base import BaseResource
from openprocurement.framework.cfaua.validation import validate_agreement_patch, validate_update_agreement_status
from openprocurement.framework.core.utils import agreementsresource
from openprocurement.framework.core.utils import apply_patch, context_unpack, save_agreement


@agreementsresource(
    name="cfaua:Agreements",
    path="/agreements/{agreement_id}",
    agreementType="cfaua",
    description="Agreements",
)
class AgreementResource(BaseResource):
    @json_view(permission="view_agreement")
    def get(self):
        return {"data": self.context.serialize("view")}

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
        validators=(
            validate_agreement_patch,
            validate_update_agreement_status,
        ),
    )
    def patch(self):
        agreement = self.context
        apply_patch(
            self.request,
            obj_name="agreement",
            save=False,
            src=self.request.validated["agreement_src"],
        )
        if save_agreement(self.request):
            self.LOGGER.info(
                "Updated agreement {}".format(agreement.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"}),
            )
            return {"data": agreement.serialize("view")}
