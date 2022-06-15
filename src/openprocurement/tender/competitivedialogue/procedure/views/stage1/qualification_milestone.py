from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.qualification_milestone import QualificationMilestoneResource
from cornice.resource import resource


@resource(
    name="{}:Tender Qualification Milestones".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender qualification milestones",
)
class TenderUAQualificationMilestoneResource(QualificationMilestoneResource):
    pass


@resource(
    name="{}:Tender Qualification Milestones".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender qualification milestones",
)
class TenderEUQualificationMilestoneResource(QualificationMilestoneResource):
    pass
