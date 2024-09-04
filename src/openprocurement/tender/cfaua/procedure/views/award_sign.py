from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.serializers.tender import (
    CFAUATenderSerializer,
)
from openprocurement.tender.core.procedure.views.award_sign import AwardSignResource


@resource(
    name="closeFrameworkAgreementUA:Tender Award Sign",
    path="/tenders/{tender_id}/awards/{award_id}/sign",
    description="Tender award sign",
    procurementMethodType="closeFrameworkAgreementUA",
)
class CFAUAAwardSignResource(AwardSignResource):
    context_objs = {
        "tender": CFAUATenderSerializer,
    }
