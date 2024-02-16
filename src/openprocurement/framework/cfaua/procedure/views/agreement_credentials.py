from cornice.resource import resource

from openprocurement.api.utils import context_unpack, json_view
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.framework.cfaua.procedure.validation import (
    validate_credentials_generate,
)
from openprocurement.framework.cfaua.procedure.views.base import AgreementBaseResource
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.procedure.validation import validate_tender_owner
from openprocurement.tender.core.procedure.utils import set_ownership


@resource(
    name=f"{CFA_UA}:Agreement Credentials",
    path="/agreements/{agreement_id}/credentials",
    agreementType=CFA_UA,
    description="Agreement Credentials",
)
class AgreementCredentialsResource(AgreementBaseResource):
    @json_view(
        permission="view_agreement",
        validators=(
            validate_tender_owner("agreement"),
            validate_credentials_generate,
        ),
    )
    def patch(self):
        agreement = self.request.validated["agreement"]

        access = set_ownership(agreement, self.request)
        if save_object(self.request, "agreement"):
            self.LOGGER.info(
                "Generate Agreement credentials {}".format(agreement["_id"]),
                extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"}),
            )
            return {"data": self.serializer_class(agreement).data, "access": access}
