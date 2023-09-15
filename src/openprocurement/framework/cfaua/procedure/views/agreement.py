# -*- coding: utf-8 -*-
from cornice.resource import resource

from openprocurement.api.auth import ACCR_3, ACCR_5
from openprocurement.api.procedure.validation import validate_input_data_from_resolved_model
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.framework.cfaua.procedure.serializers.agreement import AgreementSerializer
from openprocurement.framework.core.procedure.context import get_object
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.framework.cfaua.procedure.models.agreement import Agreement, PostAgreement
from openprocurement.framework.cfaua.procedure.state.agreement import AgreementState
from openprocurement.framework.cfaua.procedure.validation import validate_update_agreement_status
from openprocurement.framework.cfaua.procedure.views.base import AgreementBaseResource
from openprocurement.framework.core.procedure.views.agreement import AgreementsResource as BaseFrameworkAgreementResource
from openprocurement.tender.core.procedure.validation import (
    validate_patch_data,
    validate_input_data,
    validate_data_documents,
    validate_accreditation_level,
    unless_administrator,
    validate_item_owner,
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
        validators=(
            validate_input_data(PostAgreement),
            validate_data_documents(route_key="agreement_id", uid_key="id"),
            validate_accreditation_level(
                levels=(ACCR_3, ACCR_5),
                item="agreement",
                operation="creation",
                source="data"
            ),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(permission="view_agreement")
    def get(self):
        return {"data": self.serializer_class(get_object("agreement")).data}

    @json_view(
        content_type="application/json",
        validators=(
            unless_administrator(
                validate_item_owner("agreement")
            ),
            validate_input_data_from_resolved_model(),
            validate_patch_data(Agreement, item_name="agreement"),
            validate_update_agreement_status,
        ),
        permission="edit_agreement",
    )
    def patch(self):
        updated = self.request.validated["data"]
        # May be we don't need this validation as "features" field is forbidden for patching
        # if "features" in updated:
        #     if apply_data_patch(self.request.validated["agreement"]["features"], updated["features"]):
        #         self.request.errors.add("body", "features", "Can't change features")
        #         self.request.errors.status = 403
        #         raise error_handler(self.request)
        if updated:
            self.request.validated["agreement"] = updated
            if save_object(self.request, "agreement"):
                self.LOGGER.info(
                    f"Updated agreement {updated['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"})
                )
        return {"data": self.serializer_class(get_object("agreement")).data}
