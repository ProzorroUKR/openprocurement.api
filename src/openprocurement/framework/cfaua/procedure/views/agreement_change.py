from copy import deepcopy

from cornice.resource import resource

from openprocurement.api.procedure.utils import apply_data_patch, get_items, set_item
from openprocurement.api.procedure.validation import (
    validate_input_data_from_resolved_model,
    validate_patch_data_from_resolved_model,
    validate_item_owner,
    unless_administrator,
)
from openprocurement.api.utils import json_view, update_logging_context, context_unpack, raise_operation_error
from openprocurement.framework.cfaua.procedure.state.change import ChangeState
from openprocurement.framework.cfaua.procedure.utils import apply_modifications
from openprocurement.framework.cfaua.procedure.validation import (
    validate_agreement_change_add_not_in_allowed_agreement_status,
    validate_create_agreement_change,
    validate_agreement_change_update_not_in_allowed_change_status,
)
from openprocurement.framework.cfaua.procedure.views.base import AgreementBaseResource
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.api.procedure.context import get_object
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.api.procedure.serializers.base import BaseSerializer


def resolve_change(request):
    match_dict = request.matchdict
    if match_dict.get("change_id"):
        changes = get_items(request, request.validated["agreement"], "changes", match_dict["change_id"])
        request.validated["change"] = changes[0]


@resource(
    name=f"{CFA_UA}:Agreement Changes",
    collection_path="/agreements/{agreement_id}/changes",
    path="/agreements/{agreement_id}/changes/{change_id}",
    agreementType=CFA_UA,
    description="Agreement Changes",
)
class AgreementChangesResource(AgreementBaseResource):
    """Agreement changes resource"""

    serializer_class = BaseSerializer
    state_class = ChangeState

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_change(request)

    @json_view(permission="view_agreement")
    def collection_get(self):
        """Return Agreement Changes list"""
        agreement = self.request.validated["agreement"]
        data = tuple(self.serializer_class(change).data for change in agreement.get("changes", []))
        return {"data": data}

    @json_view(permission="view_agreement")
    def get(self):
        """Return Agreement Change"""
        return {"data": self.serializer_class(get_object("change")).data}

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
        validators=(
            unless_administrator(validate_item_owner("agreement")),
            validate_input_data_from_resolved_model(),
            validate_agreement_change_add_not_in_allowed_agreement_status,
            validate_create_agreement_change,
        ),
    )
    def collection_post(self):
        """Agreement Change create"""
        update_logging_context(self.request, {"change_id": "__new__"})
        agreement = self.request.validated["agreement"]

        change = self.request.validated["data"]
        self.state.on_post(change)

        if "changes" not in agreement:
            agreement["changes"] = []
        agreement["changes"].append(change)
        warnings = apply_modifications(self.request, deepcopy(agreement))

        if save_object(self.request, "agreement"):
            self.LOGGER.info(
                f"Created change {change['id']} of agreement {agreement['_id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "agreement_change_create"},
                    {"change_id": change['id'], "agreement_id": agreement['_id']},
                ),
            )
            self.request.response.status = 201
            response_data = {"data": self.serializer_class(change).data}
            if warnings:
                response_data["warnings"] = warnings
                self.LOGGER.info(
                    f"warnings: {warnings}",
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "agreement_change_create"},
                        {"change_id": change['id'], "agreement_id": agreement['_id']},
                    ),
                )
            return response_data

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
        validators=(
            unless_administrator(validate_item_owner("agreement")),
            validate_input_data_from_resolved_model(),
            validate_patch_data_from_resolved_model(item_name="change"),
            validate_agreement_change_update_not_in_allowed_change_status,
        ),
    )
    def patch(self):
        """Agreement change edit"""
        change = self.request.validated["change"]
        data = self.request.validated["data"]

        self.state.pre_patch(change, data)

        set_item(self.request.validated["agreement"], "changes", change["id"], data)
        apply_data_patch(change, data)

        # Validate or apply agreement modifications
        warnings = []
        validated_agreement = self.request.validated["agreement"]
        if data["status"] == "active":
            if not data.get("modifications"):
                raise_operation_error(self.request, "Modifications are required for change activation.")
            apply_modifications(self.request, validated_agreement)
        elif data["status"] != "cancelled":
            warnings = apply_modifications(self.request, deepcopy(validated_agreement))

        self.state.on_patch(change, data)

        if save_object(self.request, "agreement"):
            self.LOGGER.info(
                f"Updated agreement change {change['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_change_patch"}),
            )
            response_data = {"data": self.serializer_class(data).data}
            if warnings:
                response_data["warnings"] = warnings
                self.LOGGER.info(
                    f"warnings: {warnings}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_change_patch"}),
                )
            return response_data
