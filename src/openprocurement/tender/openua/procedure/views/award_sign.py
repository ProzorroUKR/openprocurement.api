from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_sign import AwardSignResource


@resource(
    name="aboveThresholdUA:Tender Award Sign",
    path="/tenders/{tender_id}/awards/{award_id}/sign",
    description="Tender award sign",
    procurementMethodType="aboveThresholdUA",
)
class UAAwardSignResource(AwardSignResource):
    pass
