from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_patch_data,
    validate_update_award_in_not_allowed_status,
)
from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.core.procedure.models.award import PatchAward, Award
from openprocurement.tender.pricequotation.procedure.state.award import AwardState
from openprocurement.tender.pricequotation.procedure.validation import validate_pq_award_owner
from openprocurement.tender.pricequotation.constants import PQ
from cornice.resource import resource


@resource(
    name="{}:Tender Awards".format(PQ),
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=PQ,
)
class PQTenderAwardResource(TenderAwardResource):
    state_class = AwardState

    @json_view(
        content_type="application/json",
        permission="edit_award",  # brokers
        validators=(
            unless_admins(
                validate_pq_award_owner,
            ),
            validate_input_data(PatchAward),
            validate_patch_data(Award, item_name="award"),
            validate_update_award_in_not_allowed_status,
        ),
    )
    def patch(self):
        return super().patch()
