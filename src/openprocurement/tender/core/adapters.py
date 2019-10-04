# -*- coding: utf-8 -*-
from openprocurement.api.adapters import ContentConfigurator


class TenderConfigurator(ContentConfigurator):
    """ Tender configuration adapter """

    name = "Tender Configurator"
    model = None

    @property
    def create_accreditations(self):
        """ tender create accreditation level """
        return self.model.create_accreditations

    @property
    def edit_accreditations(self):
        """ bid create accreditation level """
        return self.model.edit_accreditations

    # Param to configure award criteria
    # Default configuration for awarding is reversed (from lower to higher)
    # To make it work without changing all packages reverse it again =)
    # When False, awards are generated from lower to higher by value.amount
    # When True, awards are generated from higher to lower by value.amount
    reverse_awarding_criteria = False

    # Defines awarding criteria field name
    awarding_criteria_key = "amount"
