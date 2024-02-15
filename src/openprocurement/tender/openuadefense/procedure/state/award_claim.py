from openprocurement.api.constants import NO_DEFENSE_AWARD_CLAIMS_FROM
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import get_first_revision_date, raise_operation_error
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)


class DefenseAwardClaimStateMixin:
    def validate_claim_on_post(self, complaint):
        tender = get_tender()
        tender_created = get_first_revision_date(tender, default=get_now())
        if tender_created > NO_DEFENSE_AWARD_CLAIMS_FROM:
            raise_operation_error(self.request, "Can't add complaint of 'claim' type")
        super().validate_claim_on_post(complaint)


class OpenUADefenseAwardClaimState(DefenseAwardClaimStateMixin, AwardClaimStateMixin, OpenUADefenseTenderState):
    pass
