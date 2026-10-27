from cornice.resource import resource

from openprocurement.api.procedure.context import get_agreement
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.framework.cfaua.procedure.serializers.agreement import (
    AgreementSerializer,
)
from openprocurement.framework.cfaua.procedure.state.agreement import AgreementState
from openprocurement.framework.cfaua.procedure.views.base import AgreementBaseResource
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.procedure.views.agreement import (
    AgreementsResource as BaseFrameworkAgreementResource,
)


@resource(
    name=f"{CFA_UA}:Agreements",
    collection_path="/agreements",
    path="/agreements/{agreement_id}",
    description=f"{CFA_UA} agreements",
    agreementType=CFA_UA,
    accept="application/json",
)
class AgreementResource(AgreementBaseResource, BaseFrameworkAgreementResource):
    serializer_class = AgreementSerializer
    state_class = AgreementState

    @json_view(
        content_type="application/json",
        permission="create_agreement",
    )
    def collection_post(self):
        self.state.validate_agreement_post_request()
        return super().collection_post()

    @json_view(permission="view_agreement")
    def get(self):
        agreement = get_agreement()
        return {
            "data": self.serializer_class(agreement).data,
            "config": agreement["config"],
        }

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        self.state.validate_agreement_patch_request()
        updated = self.request.validated["data"]
        agreement = self.request.validated["agreement"]
        agreement_src = self.request.validated["agreement_src"]
        if updated:
            agreement = self.request.validated["agreement"] = updated
            self.state.on_patch(agreement_src, agreement)
            if save_object(self.request, "agreement"):
                self.LOGGER.info(
                    f"Updated agreement {agreement['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"}),
                )
        return {
            "data": self.serializer_class(agreement).data,
            "config": agreement["config"],
        }
