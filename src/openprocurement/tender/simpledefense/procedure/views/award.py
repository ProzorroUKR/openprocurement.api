from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_item_owner,
    validate_patch_data_simple,
    validate_patch_input_data,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.award import Award, PatchAward
from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.simpledefense.procedure.state.award import (
    SimpleDefenseAwardState,
)


@resource(
    name="simple.defense:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="simple.defense",
)
class SimpleDefenseTenderAwardResource(TenderAwardResource):
    state_class = SimpleDefenseAwardState

    @json_view(
        content_type="application/json",
        permission="edit_award",  # brokers
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_patch_input_data(PatchAward),
            validate_patch_data_simple(Award, item_name="award"),
        ),
    )
    def patch(self):
        return super().patch()
