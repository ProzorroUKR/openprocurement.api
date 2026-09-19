from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
    validate_patch_input_data,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING
from openprocurement.tender.core.procedure.models.award import PatchAward
from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.core.utils import context_view
from openprocurement.tender.esco.procedure.models.award import ESCOAward, ESCOPostAward
from openprocurement.tender.esco.procedure.serializers.award import AwardSerializer
from openprocurement.tender.esco.procedure.serializers.tender import (
    ESCOTenderSerializer,
)
from openprocurement.tender.esco.procedure.state.award import AwardState


@resource(
    name="esco:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender ESCO Awards",
    procurementMethodType="esco",
)
class EUTenderAwardResource(TenderAwardResource):
    serializer_class = AwardSerializer
    state_class = AwardState

    @json_view(
        content_type="application/json",
        permission="create_award",  # admins only
        validators=(validate_input_data(ESCOPostAward),),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_award",  # brokers
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_patch_input_data(PatchAward),
            validate_patch_data_simple(ESCOAward, item_name="award"),
        ),
    )
    def patch(self):
        return super().patch()

    @json_view(
        permission="view_tender",
    )
    @context_view(
        objs={
            "tender": (ESCOTenderSerializer, TENDER_MASK_MAPPING),
        }
    )
    def get(self):
        return super().get()
