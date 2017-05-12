# -*- coding: utf-8 -*-
from openprocurement.tender.esco.models import TenderESCOEU
from openprocurement.tender.esco.tests.base import (
    test_tender_eu_data
)


# TenderESCOEUTest


def simple_add_tender(self):
    u = TenderESCOEU(test_tender_eu_data)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb['tenderID']
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == "esco.EU"
    assert fromdb['procurementMethodType'] == "esco.EU"

    u.delete_instance(self.db)
