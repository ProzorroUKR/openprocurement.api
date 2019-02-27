# -*- coding: utf-8 -*-
from datetime import timedelta


STAND_STILL_TIME = timedelta(days=2)
STATUS4ROLE = {
    'complaint_owner': ['draft', 'answered'],
    'reviewers': ['pending'],
    'tender_owner': ['claim'],
}
BOT_NAME = 'fa_bot'
DRAFT_FIELDS = ('shortlistedFirms',)
ENQUIRY_PERIOD = timedelta(days=1)
TENDERING_DURATION = timedelta(days=3)
AUCTION_DURATION = timedelta(days=1)  # needs to be updated
COMPLAINT_DURATION = timedelta(days=1)  # needs to be updated
CLARIFICATIONS_DURATION = timedelta(days=5)  # needs to be updated
TENDER_PERIOD_MINIMAL_DURATION = timedelta(days=3)
MIN_PERIOD_UNTIL_AGREEMENT_END = timedelta(days=7)
MIN_ACTIVE_CONTRACTS = 3
MINIMAL_STEP_PERCENTAGE = 0.005

# bot switch to draft.unsuccessful messages
AGREEMENT_STATUS = 'agreements[0] status is not active'
AGREEMENT_ITEMS = 'agreements[0] items is not subset of tender items'
AGREEMENT_START_DATE = 'agreements[0].period.startDate is > tender.date'
AGREEMENT_EXPIRED = 'agreements[0] ends less than {} days'.format(MIN_PERIOD_UNTIL_AGREEMENT_END.days)
AGREEMENT_CHANGE = 'agreements[0] has pending change'
AGREEMENT_CONTRACTS = 'agreements[0] has less than {} active contracts'.format(MIN_ACTIVE_CONTRACTS)
AGREEMENT_IDENTIFIER = 'tender.procuringEntity.identifier (scheme or id), ' \
                       'doesnt match tender.agreements[0].procuringEntity.identifier (scheme of id)'
AGREEMENT_NOT_FOUND = 'agreement[0] not found in agreements'