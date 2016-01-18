# -*- coding: utf-8 -*-
import unittest
from datetime import timedelta

from openprocurement.api import ROUTE_PREFIX
from openprocurement.api.models import get_now
from openprocurement.tender.openeu.models import Tender
from openprocurement.tender.openeu.tests.base import (test_tender_data,
                                                      BaseTenderWebTest)


class TenderTest(BaseTenderWebTest):

    def test_simple_add_tender(self):
        u = Tender(test_tender_data)
        u.tenderID = "UA-X"

        assert u.id is None
        assert u.rev is None

        u.store(self.db)

        assert u.id is not None
        assert u.rev is not None

        fromdb = self.db.get(u.id)

        assert u.tenderID == fromdb['tenderID']
        assert u.doc_type == "Tender"
        assert u.procurementMethodType == "aboveThresholdEU"
        assert fromdb['procurementMethodType'] == "aboveThresholdEU"

        u.delete_instance(self.db)
