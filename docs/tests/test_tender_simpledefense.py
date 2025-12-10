import os

from openprocurement.tender.openuadefense.tests.tender import BaseTenderUAWebTest
from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

BASE_DIR = 'docs/source/tendering/simpledefense/'
TARGET_DIR = BASE_DIR + 'http/'
TARGET_CSV_DIR = BASE_DIR + 'csv/'


class SimpleDefenseResourceTest(BaseTenderUAWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = None
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="simple.defense",
            file_path=TARGET_CSV_DIR + "config.csv",
        )

    def test_docs_allowed_kind_csv(self):
        self.write_allowed_kind_csv(
            pmt="simple.defense",
            file_path=TARGET_CSV_DIR + "kind.csv",
        )
