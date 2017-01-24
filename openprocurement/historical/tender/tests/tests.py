import os.path
from jsonpointer import resolve_pointer
from openprocurement.historical.core.utils import (
    VERSION,
    PHASH,
    HASH,
    parse_hash
)
from openprocurement.api.tests.base import (
    BaseTenderWebTest,
    test_tender_data,
)
from openprocurement.historical.core.tests import test_data_with_revisions


class HistoricalTenderTestCase(BaseTenderWebTest):

    relative_to = os.path.dirname(__file__)

    def _update_doc(self):
        data = test_data_with_revisions.copy()
        tender = self.db.get(self.tender_id)
        data['_id'] = self.tender_id
        data['id'] = self.tender_id
        data['_rev'] = tender['_rev']
        self.db.save(data)

    def test_get_tender(self):
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/tenders', {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']

        response = self.app.get('/tenders/{}/historical'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], tender)

        response = self.app.get('/tenders/{}/historical?opt_jsonp=callback'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('callback({"data": {"', response.body)

        response = self.app.get('/tenders/{}/historical?opt_pretty=1'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "data": {\n        "', response.body)
        self.assertIn(VERSION, response.headers)
        self.assertEqual(response.headers[VERSION], '1')

        response = self.app.get('/tenders/{}/historical'.format(tender['id']), headers={VERSION:'0'})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], tender)

        response = self.app.get('/tenders/{}/historical'.format(tender['id']), headers={VERSION:'1000'})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], tender)

    def test_get_tender_invalid_header(self):
        for header in ['invalid', '1.5', '-1']:
            response = self.app.get('/tenders/{}/historical'.format(self.tender_id),
                                    headers={VERSION: header}, status=404)
            self.assertEqual(response.status, '404 Not Found')
            self.assertEqual(response.json['status'], 'error')
            self.assertEqual(response.json['errors'], [
                {u'description': u'Not Found', u'location': u'header', u'name': u'version'}
            ])

    def test_get_tender_versioned(self):
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/tenders', {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        self.tender_id = tender['id']
        self._update_doc()
        doc = test_data_with_revisions.copy()
        revisions = doc.pop('revisions')
        for i, rev in list(enumerate(revisions))[1:]:
            path = '/tenders/{}/historical'.format(self.tender_id)
            response = self.app.get(path, headers={VERSION:str(i)})
            tender = response.json['data']
            headers = response.headers
            self.assertEqual(headers[HASH], parse_hash(rev['rev']))
            self.assertEqual(headers[VERSION], str(i))
            self.assertEqual(headers[PHASH],
                             parse_hash(revisions[i-1].get('rev', '')))
            if rev.get('public'):
                self.assertEqual(tender['dateModified'], rev['date'])
            for ch in [r for r in rev['changes'] if rev.get('public')]:
                val = ch['value'] if ch['op'] != 'remove' else 'missing'
                if not all(p for p in ['next_check', 'shouldStartAfter'] if ch['path'] in p):
                    self.assertEqual(resolve_pointer(tender, ch['path'], 'missing'), val)

    def test_doc_type_mismatch(self):
        doc = self.db.get(self.tender_id)
        doc['doc_type'] = 'invalid'
        self.db.save(doc)
        response = self.app.get('/tenders/{}/historical'.format(self.tender_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

    def test_get_doc_invalid_hash(self):
        self._update_doc()
        response = self.app.get('/tenders/{}/historical'.format(self.tender_id),headers={VERSION:str(3)})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.get('/tenders/{}/historical'.format(self.tender_id),
                                headers={VERSION:str(3), HASH:'invalid'}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'header', u'name': u'hash'}
        ])
