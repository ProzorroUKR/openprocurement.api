# -*- coding: utf-8 -*-
from openprocurement.api.adapters import ContentConfigurator


class TenderConfigurator(ContentConfigurator):
    """ Tender configuration adapter """

    name = "Tender Configurator"
    model = None

    @property
    def create_accreditation(self):
        """ tender create accreditation level """
        return self.model.create_accreditation

    @property
    def edit_accreditation(self):
        """ bid create accreditation level """
        return self.model.edit_accreditation
