from openprocurement.api.utils import json_view, APIResource, set_ownership
from openprocurement.framework.cfaua.validation import validate_credentials_generate
from openprocurement.framework.core.utils import agreementsresource
from openprocurement.framework.core.utils import context_unpack, save_agreement


@agreementsresource(
    name="cfaua.Agreement.credentials",
    path="/agreements/{agreement_id}/credentials",
    description="Agreement credentials",
)
class AgreementCredentialsResource(APIResource):
    @json_view(permission="generate_credentials", validators=validate_credentials_generate)
    def patch(self):
        agreement = self.request.validated["agreement"]

        access = set_ownership(agreement, self.request)
        if save_agreement(self.request):
            self.LOGGER.info(
                "Generate Agreement credentials {}".format(agreement.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"}),
            )
            return {"data": agreement.serialize("view"), "access": access}
