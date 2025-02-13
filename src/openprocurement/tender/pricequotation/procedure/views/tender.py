from cornice.resource import resource

from openprocurement.api.auth import ACCR_1, ACCR_5
from openprocurement.api.procedure.context import get_object
from openprocurement.api.procedure.validation import (
    unless_administrator,
    validate_accreditation_level,
    validate_config_data,
    validate_data_documents,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.tender.core.procedure.validation import (
    validate_item_quantity,
    validate_tender_guarantee,
    validate_tender_status_allows_update,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.procedure.models.tender import (
    PatchTender,
    PostTender,
    Tender,
)
from openprocurement.tender.pricequotation.procedure.state.tender_details import (
    CatalogueTenderDetailsState,
    DPSTenderDetailsState,
    TenderDetailsState,
)


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

    state_classes = {
        ELECTRONIC_CATALOGUE_TYPE: CatalogueTenderDetailsState,
        DPS_TYPE: DPSTenderDetailsState,
    }

    def __init__(self, request, context=None):
        self.states = {}
        for agreement_type, state_class in self.state_classes.items():
            self.states[agreement_type] = state_class(request)
        super().__init__(request, context)

    @property
    def state(self):
        agreement = get_object("agreement") or {}
        return self.states.get(agreement.get("agreementType"), self.states["default"])

    @state.setter
    def state(self, value):
        self.states["default"] = value

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostTender),
            validate_config_data(),
            validate_accreditation_level(
                levels=(ACCR_1, ACCR_5),
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
            unless_administrator(
                validate_item_owner("tender"),
                validate_tender_status_allows_update("draft"),
            ),
            validate_input_data(PatchTender, none_means_remove=True),
            validate_patch_data_simple(Tender, item_name="tender"),
            validate_item_quantity,
            validate_tender_guarantee,
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()
