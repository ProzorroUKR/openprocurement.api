# -*- coding: utf-8 -*-
from datetime import timedelta
from openprocurement.tender.core.adapters import TenderConfigurator
from openprocurement.tender.cfaselectionua.constants import STATUS4ROLE


class TenderBelowThersholdConfigurator(TenderConfigurator):
    """ CFASelectionUA Tender configuration adapter """

    name = "CFASelectionUA configurator"

    # Dictionary with allowed complaint statuses for operations for each role
    allowed_statuses_for_complaint_operations_for_roles = STATUS4ROLE

    # days before agreement period ends. Not allow create procedure if less than 7 days to end agreement
    timedelta = timedelta(days=7)
