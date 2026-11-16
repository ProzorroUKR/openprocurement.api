from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_milestone import (
    BaseAwardMilestoneResource,
)
from openprocurement.tender.pricequotation.procedure.state.award_mielstone import (
    PQAwardExtensionMilestoneState,
)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
)
class PQMilestoneResource(BaseAwardMilestoneResource):
    state_class = PQAwardExtensionMilestoneState
