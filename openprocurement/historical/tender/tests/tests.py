import os.path
import logging
from jsonpointer import resolve_pointer
from openprocurement.historical.core.tests import test_data_with_revisions
from openprocurement.historical.core.utils import HEADER
from openprocurement.api.tests.base import BaseTenderWebTest, BaseWebTest


test_data = test_data_with_revisions.copy()
revisions = test_data.get('revisions')
public_revisions = [r for r in revisions if r['public']]


class BaseTenderHistoryWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_data
    setUp = BaseWebTest.setUp


class HistoricalTenderTestCase(BaseTenderHistoryWebTest):

    def setUp(self):
        super(HistoricalTenderTestCase, self).setUp()
        self.tender_id, _ = self.db.save(test_data)

    def test_get_tender(self):
        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertIn(HEADER, response.headers)
        self.assertEqual(response.headers[HEADER], str(len(public_revisions)))

    def test_get_tender_versions(self):
        for ver, rev in list(enumerate(public_revisions))[1:]:
            response = self.app.get('/tenders/{}/historical'.format(self.tender_id),
                                    headers={HEADER: str(ver)})
            self.assertEqual(response.headers[HEADER], str(ver))

            body = response.json['data']
            self.assertEqual(body['dateModified'],
                             public_revisions[int(ver) - 1]['date'])
            self.assertEqual(public_revisions[int(response.headers[HEADER])], rev)
            for p in rev['changes']:
                if not any(v in p['path'] for v in ['next_check', 'shouldStartAfter']):
                    val = p['value'] if p['op'] != 'remove' else 'missing'
                    self.assertEqual(resolve_pointer(body, p['path'], 'missing'), val)
