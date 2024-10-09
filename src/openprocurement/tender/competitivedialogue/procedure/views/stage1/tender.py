from cornice.resource import resource
from pyramid.security import Allow

from openprocurement.api.auth import ACCR_3, ACCR_5
from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_accreditation_level,
    validate_config_data,
    validate_data_documents,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.models.stage1.tender import (
    BotPatchTender,
    EUTender,
    PatchEUTender,
    PatchUATender,
    PostEUTender,
    PostUATender,
    UATender,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1TenderDetailsState,
)
from openprocurement.tender.competitivedialogue.procedure.validation import (
    unless_cd_bridge,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.models.tender import TenderConfig
from openprocurement.tender.core.procedure.validation import (
    validate_item_quantity,
    validate_tender_change_status_with_cancellation_lot_pending,
    validate_tender_guarantee,
    validate_tender_status_allows_update,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource


def conditional_eu_model(
    data,
):  # TODO: bot should use a distinct endpoint, like chronograph
    if get_request().authenticated_role == "competitive_dialogue":
        model = BotPatchTender
    else:
        model = PatchEUTender
    return model(data)


def conditional_ua_model(
    data,
):  # TODO: bot should use a distinct endpoint, like chronograph
    if get_request().authenticated_role == "competitive_dialogue":
        model = BotPatchTender
    else:
        model = PatchUATender
    return model(data)


@resource(
    name=f"{CD_EU_TYPE}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=CD_EU_TYPE,
    description=f"{CD_EU_TYPE} tenders",
    accept="application/json",
)
class CDEUTenderResource(TendersResource):
    state_class = CDStage1TenderDetailsState

    def __acl__(self):
        acl = super().__acl__()
        acl.append(
            (Allow, "g:competitive_dialogue", "edit_tender"),
        )
        return acl

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostEUTender),
            validate_config_data(TenderConfig),
            validate_accreditation_level(
                levels=(ACCR_3, ACCR_5),
                kind_central_levels=(ACCR_5,),
                item="tender",
                operation="creation",
                source="data",
            ),
            validate_data_documents(),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            unless_cd_bridge(unless_admins(unless_administrator(validate_item_owner("tender")))),
            unless_administrator(
                validate_tender_status_allows_update(
                    "draft",
                    "active.tendering",
                    "active.pre-qualification",  # state class only allows status change (pre-qualification.stand-still)
                    "active.stage2.pending",
                    "active.stage2.waiting",
                )
            ),
            validate_input_data(conditional_eu_model, none_means_remove=True),
            validate_patch_data_simple(EUTender, item_name="tender"),
            unless_administrator(validate_tender_change_status_with_cancellation_lot_pending),
            validate_item_quantity,
            validate_tender_guarantee,
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()


# ============= UA


@resource(
    name=f"{CD_UA_TYPE}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=CD_UA_TYPE,
    description=f"{CD_UA_TYPE} tenders",
    accept="application/json",
)
class CDUATenderResource(TendersResource):
    state_class = CDStage1TenderDetailsState

    def __acl__(self):
        acl = super().__acl__()
        acl.append(
            (Allow, "g:competitive_dialogue", "edit_tender"),
        )
        return acl

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostUATender),
            validate_config_data(TenderConfig),
            validate_accreditation_level(
                levels=(ACCR_3, ACCR_5),
                kind_central_levels=(ACCR_5,),
                item="tender",
                operation="creation",
                source="data",
            ),
            validate_data_documents(),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            unless_cd_bridge(unless_admins(unless_administrator(validate_item_owner("tender")))),
            unless_administrator(
                validate_tender_status_allows_update(
                    "draft",
                    "active.tendering",
                    "active.pre-qualification",  # state class only allows status change (pre-qualification.stand-still)
                    "active.stage2.pending",
                    "active.stage2.waiting",
                )
            ),
            validate_input_data(conditional_ua_model, none_means_remove=True),
            validate_patch_data_simple(UATender, item_name="tender"),
            unless_administrator(validate_tender_change_status_with_cancellation_lot_pending),
            validate_item_quantity,
            validate_tender_guarantee,
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()
