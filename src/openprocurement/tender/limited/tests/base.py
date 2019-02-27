# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import datetime
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.tender.core.utils import apply_data_patch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_data as base_data
)
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest as BaseBaseTenderWebTest
)

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

test_tender_negotiation_data_2items = deepcopy(test_tender_negotiation_data)
test_tender_negotiation_data_2items['items'] = [deepcopy(test_tender_negotiation_data_2items['items'][0]),
                                                deepcopy(test_tender_negotiation_data_2items['items'][0])]

test_tender_negotiation_quick_data = deepcopy(test_tender_data)
test_tender_negotiation_quick_data['procurementMethodType'] = "negotiation.quick"
test_tender_negotiation_quick_data['causeDescription'] = "chupacabra"
if SANDBOX_MODE:
    test_tender_negotiation_quick_data['procurementMethodDetails'] = 'quick, accelerator=1440'

test_tender_negotiation_quick_data_2items = deepcopy(test_tender_negotiation_quick_data)
test_tender_negotiation_quick_data_2items['items'] = [deepcopy(test_tender_negotiation_quick_data_2items['items'][0]),
                                                      deepcopy(test_tender_negotiation_quick_data_2items['items'][0])]

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
    initial_auth = ('Basic', ('broker', ''))
    primary_tender_status = "active"  # status, to which tender should be switched from 'draft'
    forbidden_document_modification_actions_status = "complete"  # status, in which operations with tender documents (adding, updating) are forbidden
    forbidden_contract_document_modification_actions_status = "complete"  # status, in which operations with tender's contract documents (adding, updating) are forbidden

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
