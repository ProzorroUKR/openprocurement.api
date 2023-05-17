from openprocurement.tender.core.procedure.views.qualification_milestone import QualificationMilestoneResource
from cornice.resource import resource


@resource(
    name="belowThreshold:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType="belowThreshold",
    description="belowThreshold qualification milestones",
)
class EUQualificationMilestoneResource(QualificationMilestoneResource):
    pass
