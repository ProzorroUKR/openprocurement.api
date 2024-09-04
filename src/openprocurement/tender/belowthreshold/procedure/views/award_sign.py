from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_sign import AwardSignResource


@resource(
    name="belowThreshold:Tender Award Sign",
    path="/tenders/{tender_id}/awards/{award_id}/sign",
    description="Tender award sign",
    procurementMethodType="belowThreshold",
)
class BelowThresholdAwardSignResource(AwardSignResource):
    pass
