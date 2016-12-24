from openprocurement.tender.esco.tests.base import (
    test_tender_ua_data, test_tender_eu_data,
    BaseESCOWebTest
)
from openprocurement.tender.esco.models import TenderESCOEU, TenderESCOUA


class TenderESCOUATest(BaseESCOWebTest):

    initial_auth = ('Basic', ('broker', ''))
    def test_simple_add_tender(self):
        u = TenderESCOUA(test_tender_ua_data)
        u.tenderID = "UA-X"

        assert u.id is None
        assert u.rev is None

        u.store(self.db)

        assert u.id is not None
        assert u.rev is not None

        fromdb = self.db.get(u.id)

        assert u.tenderID == fromdb['tenderID']
        assert u.doc_type == "Tender"
        assert u.procurementMethodType == "esco.UA"
        assert fromdb['procurementMethodType'] == "esco.UA"

        u.delete_instance(self.db)



class TenderESCOEUTest(BaseESCOWebTest):
    initial_auth = ('Basic', ('broker', ''))
    def test_simple_add_tender(self):
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
