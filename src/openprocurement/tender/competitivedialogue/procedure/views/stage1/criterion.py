from typing import List, Tuple

from cornice.resource import resource
from pyramid.security import Allow

from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.competitivedialogue.procedure.state.criterion import CDCriterionState
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


class BaseCDCriterionResource(BaseCriterionResource):
    def __acl__(self) -> List[Tuple[str, str, str]]:
        acl = super().__acl__()
        acl.extend([
            (Allow, "g:competitive_dialogue", "create_criterion"),
            (Allow, "g:competitive_dialogue", "edit_criterion"),
        ])
        return acl


@resource(
    name="{}:Tender Criteria".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU criteria",
)
class CDEUCriterionResource(BaseCDCriterionResource):
    state_class = CDCriterionState


@resource(
    name="{}:Tender Criteria".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA criteria",
)
class CDUACriterionResource(BaseCDCriterionResource):
    state_class = CDCriterionState
