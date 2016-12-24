# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from openprocurement.api.tests.base import (
    BaseTenderWebTest, BaseWebTest
)

from openprocurement.tender.openua.tests.base import test_tender_data as base_ua_test_data
from openprocurement.tender.openeu.tests.base import test_tender_data as base_eu_test_data


test_tender_ua_data = deepcopy(base_ua_test_data)
test_tender_ua_data['procurementMethodType'] = "esco.UA"

test_tender_eu_data = deepcopy(base_eu_test_data)
test_tender_eu_data['procurementMethodType'] = "esco.EU"


class BaseESCOWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
