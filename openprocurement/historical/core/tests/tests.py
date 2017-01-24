# -*- coding: utf-8 -*-
import unittest
import json
import os.path
from copy import copy
from pyramid.testing import DummyRequest
from jsonpointer import resolve_pointer
from openprocurement.historical.core.utils import (
    VERSION,
    HASH,
    extract_header,
    add_responce_headers,
    apply_while,
    parse_hash,
    extract_doc,
)

here = os.path.dirname(__file__)
with open(os.path.join(here, 'data.json')) as in_json:
    test_data_with_revisions = json.load(in_json)


class HistoricalTest(unittest.TestCase):

    def _dummy_request(self, data):
        request = DummyRequest()
        request.matchdict['doc_id'] = data['id']
        request.registry.db = {data['id']: data}
        setattr(request, 'errors', [])
        return request

    def test_no_header(self):
        request = DummyRequest()
        ver, h = extract_header(request)
        self.assertEqual(0, ver)
        self.assertEqual('', h)

    def test_extract_header_valid(self):
        for header in ["1", "2", "3"]:
            request = DummyRequest(headers={VERSION: header, HASH: 'test'})
            head, _hash = extract_header(request)
            self.assertEqual(int(header), head)
            self.assertEqual(_hash, 'test')

    def test_add_responce_headers_str(self):
        request = DummyRequest()
        add_responce_headers(request, '22', 'test-hash')
        self.assertIn(VERSION, request.response.headers)
        self.assertEqual('22', request.response.headers[VERSION])
        self.assertIn(HASH, request.response.headers)
        self.assertEqual('test-hash', request.response.headers[HASH])

        request = DummyRequest()
        add_responce_headers(request, 42, '')
        self.assertIn(VERSION, request.response.headers)
        self.assertEqual('42', request.response.headers[VERSION])

    def test_apply_patch(self):
        doc = test_data_with_revisions.copy()
        revisions = doc.pop('revisions')
        for i, rev in list(enumerate(revisions))[1:]:
            patched, _hash = apply_while(doc, i, revisions)
            self.assertEqual(_hash, parse_hash(rev['rev']))
            for ch in rev['changes']:
                val = ch['value'] if ch['op'] != 'remove' else 'missing'
                self.assertEqual(resolve_pointer(patched, ch['path'], 'missing'), val)

    def test_parse_hash(self):
        _hash = ''
        self.assertEqual('', parse_hash(_hash))
        _hash = '2-909f500147c5c6d6ed16357fcee10f8b'
        self.assertEqual('909f500147c5c6d6ed16357fcee10f8b', parse_hash(_hash))

    def test_extract_doc_simple(self):
        request = DummyRequest()
        request = self._dummy_request(copy(test_data_with_revisions))
        doc = extract_doc(request, 'Tender')
        self.assertDictEqual(doc, {k: v for k, v in
                                   test_data_with_revisions.items()
                                   if k != 'revisions'})

    def test_extract_doc_no_revisions(self):
        data = copy(test_data_with_revisions)
        del data['revisions']
        request = self._dummy_request(data)
        doc = extract_doc(request, 'Tender')
        self.assertDictEqual(doc, data)
        self.assertEqual(request.response.headers[VERSION], '0')
        self.assertEqual(request.response.headers[HASH], '')

    def test_extract_doc_invalid(self):
        data = test_data_with_revisions.copy()
        request = self._dummy_request(data)
        revisions = test_data_with_revisions['revisions']
        current_version = len(revisions)
        request.headers['VERSION'] = '1024'
        doc = extract_doc(request, 'Tender')
        self.assertDictEqual(doc, data)
        self.assertEqual(request.response.headers[VERSION],
                         str(current_version))
        self.assertEqual(request.response.headers[HASH],
                         '232a33826db230f4d17cb832f68b9ace')

    def test_find_date_modified(self):
        data = test_data_with_revisions.copy()
        request = self._dummy_request(data)
        request.headers[VERSION] = '11'
        doc = extract_doc(request, 'Tender')
        self.assertIn(VERSION, request.response.headers)
        self.assertEqual(request.response.headers[VERSION], '11')
        self.assertEqual(doc['dateModified'],
                         test_data_with_revisions['revisions'][11]['date'])

        data = test_data_with_revisions.copy()
        request = self._dummy_request(data)
        request.headers[VERSION] = '2'
        doc = extract_doc(request, 'Tender')
        self.assertIn(VERSION, request.response.headers)
        self.assertEqual(request.response.headers[VERSION], '2')
        self.assertEqual(doc['dateModified'],
                         test_data_with_revisions['revisions'][1]['date'])
