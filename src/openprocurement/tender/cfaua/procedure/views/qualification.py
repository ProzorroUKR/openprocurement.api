from openprocurement.tender.core.procedure.views.qualification import TenderQualificationResource
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Qualification",
    collection_path="/tenders/{tender_id}/qualifications",
    path="/tenders/{tender_id}/qualifications/{qualification_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="TenderEU Qualification",
)
class TenderUAQualificationResource(TenderQualificationResource):
    pass
