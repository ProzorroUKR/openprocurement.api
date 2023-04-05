from openprocurement.api.utils import json_view
from openprocurement.api.auth import ACCR_1, ACCR_5, ACCR_2
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.models.tender import TenderConfig
from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.pricequotation.procedure.models.tender import (
    PostTender,
    PatchTender,
    PatchPQBotTender,
    Tender,
)
from openprocurement.tender.pricequotation.procedure.state.tender_details import TenderDetailsState
from openprocurement.tender.pricequotation.constants import PQ, PQ_KINDS
from openprocurement.tender.pricequotation.procedure.validation import (
    unless_administrator_or_bots,
    validate_tender_criteria_existence,
)
from openprocurement.tender.core.procedure.validation import (
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
    validate_data_documents,
    validate_accreditation_level,
    validate_tender_status_allows_update,
    validate_item_quantity,
    validate_tender_guarantee,
    validate_config_data,
)
from cornice.resource import resource
from pyramid.security import Allow


def conditional_model(data):  # TODO: bot should use a distinct endpoint, like chronograph
    if get_request().authenticated_role == "bots":
        model = PatchPQBotTender
    else:
        model = PatchTender
    return model(data)


@resource(
    name=f"{PQ}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=PQ,
    description=f"{PQ} tenders",
    accept="application/json",
)
class PriceQuotationTenderResource(TendersResource):
    state_class = TenderDetailsState

    def __acl__(self):
        acl = super().__acl__()
        acl.append(
            (Allow, "g:bots", "edit_tender"),  # TODO: bot should use a distinct endpoint, like chronograph
        )
        return acl

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostTender),
            validate_config_data(TenderConfig, obj_name="tender"),
            validate_accreditation_level(
                levels=(ACCR_1, ACCR_5),
                kind_central_levels=(ACCR_5,),
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
            unless_administrator_or_bots(
                validate_item_owner("tender"),
                validate_tender_status_allows_update("draft"),
            ),
            validate_input_data(conditional_model, none_means_remove=True),
            validate_patch_data_simple(Tender, item_name="tender"),
            # validate_accreditation_level(
            #     levels=(ACCR_2,),
            #     item="tender",
            #     operation="update",
            # ),
            validate_tender_criteria_existence,
            validate_item_quantity,
            validate_tender_guarantee,
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()
