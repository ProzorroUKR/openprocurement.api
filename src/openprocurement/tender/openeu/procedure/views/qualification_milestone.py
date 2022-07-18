from openprocurement.tender.core.procedure.views.qualification_milestone import QualificationMilestoneResource
from cornice.resource import resource


@resource(
    name="aboveThresholdEU:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU qualification milestones",
)
class EUQualificationMilestoneResource(QualificationMilestoneResource):
    pass
