from openprocurement.api.utils import json_view
from openprocurement.agreement.core.resource import (
    AgreementsResource,
    agreements_resource
    )
from openprocurement.agreement.core.utils import (
    apply_patch,
    context_unpack,
    save_agreement
)


@agreements_resource(
    name='cfaua:Agreement',
    path='/agreements/{agreement_id}',
    agreementType='cfaua'
)
class CFAgreementAPIResource(AgreementsResource):

    @json_view(permission='view_agreement')
    def get(self):
        return {
            "data": self.context.serialize("view")
        }

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
        validators=()
    )
    def patch(self):
        agreement = self.context
        apply_patch(
            self.request,
            save=False,
            src=self.request.validated['agreement_src']
        )
        if save_agreement(self.request):
            self.LOGGER.info(
                "Updated agreement {}".format(agreement.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"})
            )
            return {
                "data": agreement.serialize('view')
            }