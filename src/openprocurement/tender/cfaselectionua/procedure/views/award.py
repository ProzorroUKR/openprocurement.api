from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.cfaselectionua.procedure.state.award import CFASelectionAwardState
from openprocurement.tender.core.procedure.views.award import TenderAwardResource


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
)
class UATenderAwardResource(TenderAwardResource):
    state_class = CFASelectionAwardState
