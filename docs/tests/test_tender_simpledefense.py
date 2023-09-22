# -*- coding: utf-8 -*-
import os

from openprocurement.tender.openuadefense.tests.tender import BaseTenderUAWebTest

from tests.base.constants import (
    DOCS_URL,
    AUCTIONS_URL,
)
from tests.base.test import (
    DumpsWebTestApp,
    MockWebTestMixin,
)
from tests.test_tender_config import TenderConfigCSVMixin


TARGET_DIR = 'docs/source/tendering/simpledefense/http/'
TARGET_CSV_DIR = 'docs/source/tendering/simpledefense/csv/'


class SimpleDefenseResourceTest(BaseTenderUAWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = None
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super(SimpleDefenseResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(SimpleDefenseResourceTest, self).tearDown()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="simple.defense",
            file_path=TARGET_CSV_DIR + "config.csv",
        )
