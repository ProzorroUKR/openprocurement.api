from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_sign import AwardSignResource


@resource(
    name="reporting:Tender Award Sign",
    path="/tenders/{tender_id}/awards/{award_id}/sign",
    description="Tender award sign",
    procurementMethodType="reporting",
)
class ReportingAwardSignResource(AwardSignResource):
    pass


@resource(
    name="negotiation:Tender Award Sign",
    path="/tenders/{tender_id}/awards/{award_id}/sign",
    description="Tender award sign",
    procurementMethodType="negotiation",
)
class NegotiationAwardSignResource(AwardSignResource):
    pass


@resource(
    name="negotiation.quick:Tender Award Sign",
    path="/tenders/{tender_id}/awards/{award_id}/sign",
    description="Tender award sign",
    procurementMethodType="negotiation.quick",
)
class NegotiationQuickAwardSignResource(AwardSignResource):
    pass
