# -*- coding: utf-8 -*-
from openprocurement.tender.core.adapters import TenderConfigurator
from openprocurement.tender.cfaselectionua.constants import (
    STATUS4ROLE,
    MIN_PERIOD_UNTIL_AGREEMENT_END,
    MIN_ACTIVE_CONTRACTS,
)


class TenderBelowThersholdConfigurator(TenderConfigurator):
    """ CFASelectionUA Tender configuration adapter """

    name = "CFASelectionUA configurator"

    # Dictionary with allowed complaint statuses for operations for each role
    allowed_statuses_for_complaint_operations_for_roles = STATUS4ROLE

    # days before agreement period ends. Not allow create procedure if less than 7 days to end agreement
    agreement_expired_until = MIN_PERIOD_UNTIL_AGREEMENT_END
    # if bot patches tender with agreement with less than 3 active contracts, tender -> draft.unsuccessful
    min_active_contracts = MIN_ACTIVE_CONTRACTS
