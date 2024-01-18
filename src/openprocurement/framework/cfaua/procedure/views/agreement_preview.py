from cornice.resource import resource

from openprocurement.api.utils import json_view, context_unpack
from openprocurement.framework.cfaua.procedure.views.base import AgreementBaseResource
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.framework.cfaua.procedure.utils import apply_modifications
from openprocurement.api.procedure.context import get_object


@resource(
    name=f"{CFA_UA}:Agreement Preview",
    path="/agreements/{agreement_id}/preview",
    agreementType=CFA_UA,
    description="Agreement Preview",
)
class AgreementPreviewResource(AgreementBaseResource):
    @json_view(permission="view_agreement")
    def get(self):
        agreement = get_object("agreement")
        if not agreement.get("changes") or agreement["changes"][-1]["status"] != "pending":
            return {"data": self.serializer_class(agreement).data}

        warnings = apply_modifications(self.request, agreement)
        response_data = {"data": self.serializer_class(agreement).data}
        if warnings:
            response_data["warnings"] = warnings
            self.LOGGER.info(
                f"warnings: {warnings}", extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_preview"})
            )
        return response_data
