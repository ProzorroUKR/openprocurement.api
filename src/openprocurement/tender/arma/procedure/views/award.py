from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.award import ARMAAwardState
from openprocurement.tender.core.procedure.views.award import TenderAwardResource


@resource(
    name=f"{COMPLEX_ASSET_ARMA}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=COMPLEX_ASSET_ARMA,
)
class AwardResource(TenderAwardResource):
    state_class = ARMAAwardState
