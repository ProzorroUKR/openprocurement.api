# -*- coding: utf-8 -*-


class TenderInitializeEvent(object):
    """ Tender initialization event. """

    def __init__(self, tender):
        self.tender = tender
