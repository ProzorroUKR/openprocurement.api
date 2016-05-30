# -*- coding: utf-8 -*-
import unittest
from datetime import timedelta
from openprocurement.api.models import get_now, SANDBOX_MODE
from openprocurement.api import ROUTE_PREFIX
from openprocurement.api.tests.base import BaseWebTest, test_organization
from openprocurement.tender.competitivedialogue.models import TenderUA, TenderEU
from openprocurement.tender.openua.tests.base import test_tender_data as test_tender_data_ua
from openprocurement.tender.openeu.tests.base import test_tender_data as test_tender_data_eu
from copy import deepcopy


class CompetitiveDialogTest(BaseWebTest):

    def test_simple_add_tender_ua(self):
        test_tender_data_ua['procurementMethodType'] = "competitiveDialogue.aboveThresholdUA"
        u = TenderUA(test_tender_data_ua)
        u.tenderID = "UA-X"

        assert u.id is None
        assert u.rev is None

        u.store(self.db)

        assert u.id is not None
        assert u.rev is not None

        fromdb = self.db.get(u.id)

        assert u.tenderID == fromdb['tenderID']
        assert u.doc_type == "Tender"
        assert u.procurementMethodType == "competitiveDialogue.aboveThresholdUA"

        u.delete_instance(self.db)

    def test_simple_add_tender_eu(self):
        test_tender_data_eu['procurementMethodType'] = "competitiveDialogue.aboveThresholdEU"
        u = TenderEU(test_tender_data_eu)
        u.tenderID = "UA-X"

        assert u.id is None
        assert u.rev is None

        u.store(self.db)

        assert u.id is not None
        assert u.rev is not None

        fromdb = self.db.get(u.id)

        assert u.tenderID == fromdb['tenderID']
        assert u.doc_type == "Tender"
        assert u.procurementMethodType == "competitiveDialogue.aboveThresholdEU"

        u.delete_instance(self.db)