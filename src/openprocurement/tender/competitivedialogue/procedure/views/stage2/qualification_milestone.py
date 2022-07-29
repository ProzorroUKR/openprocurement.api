from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE
from openprocurement.tender.core.procedure.views.qualification_milestone import QualificationMilestoneResource
from cornice.resource import resource


@resource(
    name="{}:Tender Qualification Milestones".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender qualification milestones",
)
class CDStage2UAQualificationMilestoneResource(QualificationMilestoneResource):
    pass
