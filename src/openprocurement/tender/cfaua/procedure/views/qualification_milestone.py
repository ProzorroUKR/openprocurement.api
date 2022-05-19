from openprocurement.tender.core.procedure.views.qualification_milestone import QualificationMilestoneResource
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender qualification milestones",
)
class CDStage2UAAwardMilestoneResource(QualificationMilestoneResource):
    pass
