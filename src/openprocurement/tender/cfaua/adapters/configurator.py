from openprocurement.api.constants import TZ
from openprocurement.tender.cfaua.constants import (
    TENDERING_DURATION,
    PREQUALIFICATION_COMPLAINT_STAND_STILL,
    QUESTIONS_STAND_STILL,
    MIN_BIDS_NUMBER,
    QUALIFICATION_COMPLAINT_STAND_STILL,
    TENDERING_EXTRA_PERIOD,
    CLARIFICATIONS_UNTIL_PERIOD,
    MAX_AGREEMENT_PERIOD,
)
from openprocurement.tender.cfaua.models.tender import CloseFrameworkAgreementUA
from openprocurement.tender.core.adapters import TenderConfigurator
from openprocurement.tender.openua.constants import (
    STATUS4ROLE,
    CLAIM_SUBMIT_TIME,
    COMPLAINT_SUBMIT_TIME,
    ENQUIRY_STAND_STILL_TIME,
)


class CloseFrameworkAgreementUAConfigurator(TenderConfigurator):
    """ AboveThresholdEU Tender configuration adapter """

    def __init__(self, *args, **kwargs):
        if len(args) == 2:
            self.context, self.request = args
        else:
            self.context = args[0]

    tz = TZ
    name = "CloseFrameworkAgreementUA Tender configurator"
    model = CloseFrameworkAgreementUA

    # duration of tendering period. timedelta object.
    tendering_period_duration = TENDERING_DURATION

    # duration of tender period extension. timedelta object
    tendering_period_extra = TENDERING_EXTRA_PERIOD

    # duration of pre-qualification stand-still period. timedelta object.
    prequalification_complaint_stand_still = PREQUALIFICATION_COMPLAINT_STAND_STILL

    # duration of qualification stand-still period. timedelta object.
    qualification_complaint_stand_still = QUALIFICATION_COMPLAINT_STAND_STILL

    # duration of questions stand-still period. timedelta object.
    questions_stand_still = QUESTIONS_STAND_STILL

    # duration of enquiry stand-still period. timedelta object.
    enquiry_stand_still = ENQUIRY_STAND_STILL_TIME

    block_tender_complaint_status = model.block_tender_complaint_status
    block_complaint_status = model.block_complaint_status

    # Dictionary with allowed complaint statuses for operations for each role
    allowed_statuses_for_complaint_operations_for_roles = STATUS4ROLE

    # Tender claims should be sumbitted not later then "tender_claim_submit_time" days before tendering period end. Timedelta object
    tender_claim_submit_time = CLAIM_SUBMIT_TIME

    # Tender complaints should be sumbitted not later then "tender_claim_submit_time" days before tendering period end. Timedelta object
    tender_complaint_submit_time = COMPLAINT_SUBMIT_TIME

    min_bids_number = MIN_BIDS_NUMBER

    # Duration of documents with prices per unit upload

    clarifications_until_period = CLARIFICATIONS_UNTIL_PERIOD

    max_agreement_period = MAX_AGREEMENT_PERIOD
