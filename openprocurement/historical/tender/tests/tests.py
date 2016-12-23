import os.path
from openprocurement.historical.core.tests import test_data_with_revisions
from openprocurement.api.tests.base import BaseTenderWebTest as BaseBaseTenderWebTest, test_tender_data, BaseTenderWebTest


class BaseTenderHistoryWebTest(BaseBaseTenderWebTest):
    relative_to = os.path.dirname(__file__)


class HistoricalTenderTestCase(BaseTenderHistoryWebTest):
    setUp = BaseTenderWebTest.setUp
    #initial_data = test_data_with_revisions
    def setUp(self):
        super(HistoricalTenderTestCase, self).setUp()
        test_data_with_revisions['doc_type'] = 'Tender'
        test_data_with_revisions['_id'] = test_data_with_revisions['id']
        self.doc_id, _ = self.db.save(test_data_with_revisions)

    def test_get_tender(self):
        #self.app.post_json(self
        #response = self.app.post_json('/tenders', {'data': test_tender_data})
        response = self.app.get('/tenders/{}/historical'.format(self.doc_id))
        #response = self.app.get('/tenders/{}/historical'.format(self.doc_id))
        self.assertEqual(response.status, '200 OK')
        #self.assertEqual(len(response.json['data']), 1)
