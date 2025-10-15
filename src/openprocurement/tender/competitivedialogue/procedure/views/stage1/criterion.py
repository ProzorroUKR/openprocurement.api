from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.criterion import (
    CDCriterionState,
)
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource


@resource(
    name="{}:Tender Criteria".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU criteria",
)
class CDEUCriterionResource(BaseCriterionResource):
    state_class = CDCriterionState


@resource(
    name="{}:Tender Criteria".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA criteria",
)
class CDUACriterionResource(BaseCriterionResource):
    state_class = CDCriterionState
