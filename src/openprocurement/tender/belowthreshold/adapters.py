# -*- coding: utf-8 -*-
from openprocurement.tender.core.adapters import TenderConfigurator
from openprocurement.tender.belowthreshold.constants import STATUS4ROLE


class TenderBelowThersholdConfigurator(TenderConfigurator):
    """ BelowThreshold Tender configuration adapter """

    name = "BelowThreshold configurator"

    # Dictionary with allowed complaint statuses for operations for each role
    allowed_statuses_for_complaint_operations_for_roles = STATUS4ROLE
