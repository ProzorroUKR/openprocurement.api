from cornice.resource import resource

from openprocurement.tender.cfaselectionua.procedure.state.award import AwardState
from openprocurement.tender.core.procedure.views.award import TenderAwardResource


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
)
class UATenderAwardResource(TenderAwardResource):
    state_class = AwardState
