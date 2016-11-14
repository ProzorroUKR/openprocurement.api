# -*- coding: utf-8 -*-
import os
import webtest
from copy import deepcopy
from datetime import datetime, timedelta
from openprocurement.api.models import SANDBOX_MODE
from openprocurement.api.utils import apply_data_patch
from openprocurement.api.tests.base import test_tender_data as base_data
from openprocurement.api.tests.base import BaseTenderWebTest as BaseBaseTenderWebTest
from openprocurement.api.tests.base import test_organization

now = datetime.now()
test_tender_data = base_data.copy()
del test_tender_data['enquiryPeriod']
del test_tender_data['tenderPeriod']
del test_tender_data['minimalStep']

test_tender_data['procurementMethodType'] = "reporting"
test_tender_data['procuringEntity']["kind"] = "general"
if SANDBOX_MODE:
    test_tender_data['procurementMethodDetails'] = 'quick, accelerator=1440'

test_tender_negotiation_data = deepcopy(test_tender_data)
test_tender_negotiation_data['procurementMethodType'] = "negotiation"
test_tender_negotiation_data['cause'] = "twiceUnsuccessful"
test_tender_negotiation_data['causeDescription'] = "chupacabra"
if SANDBOX_MODE:
    test_tender_negotiation_data['procurementMethodDetails'] = 'quick, accelerator=1440'

test_tender_negotiation_quick_data = deepcopy(test_tender_data)
test_tender_negotiation_quick_data['procurementMethodType'] = "negotiation.quick"
test_tender_negotiation_quick_data['causeDescription'] = "chupacabra"
if SANDBOX_MODE:
    test_tender_negotiation_quick_data['procurementMethodDetails'] = 'quick, accelerator=1440'

test_lots = [
    {
        'title': 'lot title',
        'description': 'lot description',
        'value': deepcopy(test_tender_negotiation_data['value'])
    }
]

class BaseTenderWebTest(BaseBaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        super(BaseBaseTenderWebTest, self).setUp()
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db
        if self.docservice:
            self.setUpDS()

    def tearDown(self):
        if self.docservice:
            self.tearDownDS()
        del self.couchdb_server[self.db.name]

    def set_status(self, status, extra=None):
        data = {'status': status}

        if extra:
            data.update(extra)

        tender = self.db.get(self.tender_id)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)

        # authorization = self.app.authorization
        #self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        #self.app.authorization = authorization
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        return response


class BaseTenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(BaseTenderContentWebTest, self).setUp()
        self.create_tender()
