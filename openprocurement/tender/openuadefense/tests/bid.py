# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_organization
)
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderBidDocumentResourceTest
    not_found,
    # TenderBidderBatchDocumentWithDSResourceTest
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
)

from openprocurement.tender.openua.tests.base import test_bids
from openprocurement.tender.openua.tests.bid import (
    TenderBidResourceTestMixin,
    TenderBidDocumentResourceTestMixin
)
from openprocurement.tender.openua.tests.bid_blanks import (
    # TenderBidFeaturesResourceTest
    features_bidder,
    features_bidder_invalid,
    # TenderBidDocumentWithDSResourceTest
    create_tender_bidder_document_json,
    put_tender_bidder_document_json,
)

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_features_tender_ua_data
)


class TenderBidResourceTest(BaseTenderUAContentWebTest, TenderBidResourceTestMixin):
    initial_status = 'active.tendering'
    test_bids_data = test_bids  # TODO: change attribute identifier
    author_data = test_organization


class TenderBidFeaturesResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_features_tender_ua_data
    initial_status = 'active.tendering'

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentResourceTest(BaseTenderUAContentWebTest, TenderBidDocumentResourceTestMixin):
    initial_status = 'active.tendering'
    author_data = test_organization

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'tenderers': [test_organization], "value": {"amount": 500}, 'selfEligible': True, 'selfQualified': True}})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']

    test_not_found = snitch(not_found)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_create_tender_bidder_document_json = snitch(create_tender_bidder_document_json)
    test_put_tender_bidder_document_json = snitch(put_tender_bidder_document_json)


class TenderBidderBatchDocumentsWithDSResourceTest(BaseTenderUAContentWebTest):
    docservice = True
    initial_status = 'active.tendering'

    bid_data_wo_docs = {'tenderers': [test_organization],
                        'value': {'amount': 500},
                        'selfEligible': True,
                        'selfQualified': True,
                        'documents': []
        }

    create_tender_bid_with_document_invalid = snitch(create_tender_bid_with_document_invalid)
    create_tender_bid_with_document = snitch(create_tender_bid_with_document)
    create_tender_bid_with_documents = snitch(create_tender_bid_with_documents)


class TenderBidderBatchDocumentsWithDSResourceTest(BaseTenderUAContentWebTest):
    docservice = True
    initial_status = 'active.tendering'

    def test_create_tender_bidder_with_document_invalid(self):
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
            {'data': {
                'tenderers': [test_organization],
                'value': {'amount': 500},
                'selfEligible': True,
                'selfQualified': True,
                'documents': [{
                    'title': 'name.doc',
                    'url': 'http://invalid.docservice.url/get/uuid',
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword'
                }]
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add document only from document service.")

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
            {'data': {
                'tenderers': [test_organization],
                'value': {'amount': 500},
                'selfEligible': True,
                'selfQualified': True,
                'documents': [{
                    'title': 'name.doc',
                    'url': '/'.join(self.generate_docservice_url().split('/')[:4]),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword'
                }]
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add document only from document service.")

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
            {'data': {
                'tenderers': [test_organization],
                'value': {'amount': 500},
                'selfEligible': True,
                'selfQualified': True,
                'documents': [{
                    'title': 'name.doc',
                    'url': self.generate_docservice_url().split('?')[0],
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword'
                }]
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add document only from document service.")

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
            {'data': {
                'tenderers': [test_organization],
                'value': {'amount': 500},
                'selfEligible': True,
                'selfQualified': True,
                'documents': [{
                    'title': 'name.doc',
                    'url': self.generate_docservice_url(),
                    'format': 'application/msword'
                }]
            }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["location"], "documents")
        self.assertEqual(response.json['errors'][0]["name"], "hash")
        self.assertEqual(response.json['errors'][0]["description"], "This field is required.")

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
            {'data': {
                'tenderers': [test_organization],
                'value': {'amount': 500},
                'selfEligible': True,
                'selfQualified': True,
                'documents': [{
                    'title': 'name.doc',
                    'url': self.generate_docservice_url().replace(self.app.app.registry.keyring.keys()[-1], '0' * 8),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword'
                }]
            }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Document url expired.")

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
            {'data': {
                'tenderers': [test_organization],
                'value': {'amount': 500},
                'selfEligible': True,
                'selfQualified': True,
                'documents': [{
                    'title': 'name.doc',
                    'url': self.generate_docservice_url().replace("Signature=", "Signature=ABC"),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword'
                }]
            }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Document url signature invalid.")

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
            {'data': {
                'tenderers': [test_organization],
                'value': {'amount': 500},
                'selfEligible': True,
                'selfQualified': True,
                'documents': [{
                    'title': 'name.doc',
                    'url': self.generate_docservice_url().replace("Signature=", "Signature=bw%3D%3D"),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword'
                }]
            }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Document url invalid.")

    def test_create_tender_bidder_with_document(self):
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
            {'data': {
                'tenderers': [test_organization],
                'value': {'amount': 500},
                'selfEligible': True,
                'selfQualified': True,
                'documents': [{
                    'title': 'name.doc',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword'
                }]
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        self.assertEqual(bidder['tenderers'][0]['name'], test_organization['name'])
        self.assertIn('id', bidder)
        self.bid_id = bidder['id']
        self.bid_token = response.json['access']['token']
        self.assertIn(bidder['id'], response.headers['Location'])
        document = bidder['documents'][0]
        self.assertEqual('name.doc', document["title"])
        key = document["url"].split('?')[-1].split('=')[-1]

        response = self.app.get('/tenders/{}/bids/{}/documents'.format(self.tender_id, self.bid_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid documents in current (active.tendering) tender status")

        response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(document['id'], response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/bids/{}/documents?all=true&acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(document['id'], response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/bids/{}/documents/{}?download=some_id&acc_token={}'.format(
            self.tender_id, self.bid_id, document['id'], self.bid_token), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}'.format(
            self.tender_id, self.bid_id, document['id'], key), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

        response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.tender_id, self.bid_id, document['id'], key, self.bid_token))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)

        response = self.app.get('/tenders/{}/bids/{}/documents/{}'.format(
            self.tender_id, self.bid_id, document['id']), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

        response = self.app.get('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, document['id'], self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(document['id'], response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

    def test_create_tender_bidder_with_documents(self):
        dateModified = self.db.get(self.tender_id).get('dateModified')

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
            {'data': {
                'tenderers': [test_organization],
                'value': {'amount': 500},
                'selfEligible': True,
                'selfQualified': True,
                'documents': [
                    {
                        'title': 'first.doc',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/msword'
                    },
                    {
                        'title': 'second.doc',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/msword'
                    },
                    {
                        'title': 'third.doc',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/msword'
                    }]
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        self.assertEqual(bidder['tenderers'][0]['name'], test_organization['name'])
        self.assertIn('id', bidder)
        self.bid_id = bidder['id']
        self.bid_token = response.json['access']['token']
        self.assertIn(bidder['id'], response.headers['Location'])
        documents = bidder['documents']
        ids = [doc['id'] for doc in documents]
        self.assertEqual(['first.doc', 'second.doc', 'third.doc'], [document["title"] for document in documents])

        response = self.app.get('/tenders/{}/bids/{}/documents'.format(self.tender_id, self.bid_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid documents in current (active.tendering) tender status")

        response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json["data"]), 3)
        self.assertEqual(ids, [doc['id'] for doc in response.json["data"]])

        response = self.app.get('/tenders/{}/bids/{}/documents?all=true&acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json["data"]), 3)
        self.assertEqual(ids, [doc['id'] for doc in response.json["data"]])

        for index, document in enumerate(documents):
            key = document["url"].split('?')[-1].split('=')[-1]

            response = self.app.get('/tenders/{}/bids/{}/documents/{}?download=some_id&acc_token={}'.format(
                self.tender_id, self.bid_id, document['id'], self.bid_token), status=404)
            self.assertEqual(response.status, '404 Not Found')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['status'], 'error')
            self.assertEqual(response.json['errors'], [
                {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
            ])

            response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}'.format(
                self.tender_id, self.bid_id, document['id'], key), status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

            response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
                self.tender_id, self.bid_id, document['id'], key, self.bid_token))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertIn('Expires=', response.location)

            response = self.app.get('/tenders/{}/bids/{}/documents/{}'.format(
                self.tender_id, self.bid_id, document['id']), status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

            response = self.app.get('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                self.tender_id, self.bid_id, document['id'], self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(document['id'], response.json["data"]["id"])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
