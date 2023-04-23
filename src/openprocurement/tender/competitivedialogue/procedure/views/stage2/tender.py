from openprocurement.api.utils import json_view
from openprocurement.api.auth import ACCR_5, ACCR_COMPETITIVE
from openprocurement.tender.core.procedure.models.tender import TenderConfig
from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDEUTenderDetailsState,
    CDUATenderDetailsState,
)
from openprocurement.tender.competitivedialogue.procedure.models.stage2.tender import (
    PostEUTender,
    PatchEUTender,
    EUTender,
    PostUATender,
    PatchUATender,
    UATender,
    BotPatchTender,
)
from openprocurement.tender.openeu.procedure.serializers.tender import TenderEUSerializer
from openprocurement.tender.core.procedure.serializers.tender import TenderBaseSerializer
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
    STAGE_2_EU_DEFAULT_CONFIG,
    STAGE_2_UA_DEFAULT_CONFIG,
)
from openprocurement.tender.competitivedialogue.procedure.validation import (
    unless_cd_bridge,
    validate_cd2_allowed_patch_fields,
)
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    unless_administrator,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
    validate_data_documents,
    validate_accreditation_level,
    validate_tender_status_allows_update,
    validate_tender_change_status_with_cancellation_lot_pending,
    validate_config_data,
)
from cornice.resource import resource
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS


def stage2_acl():
    acl = [
        (Allow, Everyone, "view_tender"),
        (Allow, "g:competitive_dialogue", "create_tender"),
        (Allow, "g:competitive_dialogue", "edit_tender"),
        (Allow, "g:brokers", "edit_tender"),
        (Allow, "g:Administrator", "edit_tender"),
        (Allow, "g:admins", ALL_PERMISSIONS),  # some tests use this, idk why
    ]
    return acl


def conditional_eu_model(data):  # TODO: bot should use a distinct endpoint, like chronograph
    if get_request().authenticated_role == "competitive_dialogue":
        model = BotPatchTender
    else:
        model = PatchEUTender
    return model(data)


def conditional_ua_model(data):  # TODO: bot should use a distinct endpoint, like chronograph
    if get_request().authenticated_role == "competitive_dialogue":
        model = BotPatchTender
    else:
        model = PatchUATender
    return model(data)


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description=f"{STAGE_2_EU_TYPE} tenders",
    accept="application/json",
)
class TenderStage2UEResource(TendersResource):

    serializer_class = TenderEUSerializer
    state_class = CDEUTenderDetailsState

    def __acl__(self):
        return stage2_acl()

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostEUTender),
            validate_config_data(TenderConfig, obj_name="tender", default=STAGE_2_EU_DEFAULT_CONFIG),
            validate_accreditation_level(
                levels=(ACCR_COMPETITIVE,),
                kind_central_levels=(ACCR_COMPETITIVE, ACCR_5),
                item="tender",
                operation="creation",
                source="data"
            ),
            validate_data_documents(),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            unless_cd_bridge(unless_admins(unless_administrator(
                validate_item_owner("tender")
            ))),
            unless_administrator(
                validate_tender_status_allows_update(
                    "draft",
                    "draft.stage2",
                    "active.tendering",
                    "active.pre-qualification",
                )
            ),
            validate_input_data(conditional_eu_model, none_means_remove=True),
            unless_administrator(unless_cd_bridge(validate_cd2_allowed_patch_fields)),  # TODO make models only allow these fields
            validate_patch_data_simple(EUTender, item_name="tender"),
            # validate_accreditation_level(
            #     levels=(ACCR_COMPETITIVE, ACCR_4),
            #     item="tender",
            #     operation="update",
            # ),

            unless_administrator(validate_tender_change_status_with_cancellation_lot_pending),
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()


# ============= UA

@resource(
    name=f"{STAGE_2_UA_TYPE}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description=f"{STAGE_2_UA_TYPE} tenders",
    accept="application/json",
)
class TenderStage2UAResource(TendersResource):

    serializer_class = TenderBaseSerializer
    state_class = CDUATenderDetailsState

    def __acl__(self):
        return stage2_acl()

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostUATender),
            validate_config_data(TenderConfig, obj_name="tender", default=STAGE_2_UA_DEFAULT_CONFIG),
            validate_accreditation_level(
                levels=(ACCR_COMPETITIVE,),
                kind_central_levels=(ACCR_COMPETITIVE, ACCR_5),
                item="tender",
                operation="creation",
                source="data"
            ),
            validate_data_documents(),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            unless_cd_bridge(unless_admins(unless_administrator(
                validate_item_owner("tender")
            ))),
            unless_administrator(
                validate_tender_status_allows_update(
                    "draft",
                    "draft.stage2",
                    "active.tendering",
                )
            ),
            validate_input_data(conditional_ua_model, none_means_remove=True),
            unless_administrator(unless_cd_bridge(validate_cd2_allowed_patch_fields)),  # TODO make models only allow these fields
            validate_patch_data_simple(UATender, item_name="tender"),
            # validate_accreditation_level(
            #     levels=(ACCR_COMPETITIVE, ACCR_4),
            #     item="tender",
            #     operation="update",
            # ),
            unless_administrator(validate_tender_change_status_with_cancellation_lot_pending),
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()
