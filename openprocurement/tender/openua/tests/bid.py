# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_organization,
)
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderBidDocumentResourceTest
    not_found,
    # TenderBidderBatchDocumentWithDSResourceTest
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
)

from openprocurement.tender.openua.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_data,
    test_features_tender_ua_data,
)
from openprocurement.tender.openua.tests.bid_blanks import (
    # TenderBidResourceTest
    create_tender_biddder_invalid,
    create_tender_bidder,
    patch_tender_bidder,
    get_tender_bidder,
    delete_tender_bidder,
    deleted_bid_is_not_restorable,
    deleted_bid_do_not_locks_tender_in_state,
    get_tender_tenderers,
    bid_Administrator_change,
    draft1_bid,
    draft2_bids,
    bids_invalidation_on_tender_change,
    bids_activation_on_tender_documents,
    # TenderBidFeautreResourceTest
    features_bidder,
    features_bidder_invalid,
    # TenderBidDocumentResourceTest
    create_tender_bidder_document,
    put_tender_bidder_document,
    patch_tender_bidder_document,
    create_tender_bidder_document_nopending,
    # TenderBidDocumentWithDSResourceTest
    create_tender_bidder_document_json,
    put_tender_bidder_document_json,
)


class TenderBidResourceTestMixin(object):
    test_create_tender_biddder_invalid = snitch(create_tender_biddder_invalid)
    test_create_tender_bidder = snitch(create_tender_bidder)
    test_patch_tender_bidder = snitch(patch_tender_bidder)
    test_get_tender_bidder = snitch(get_tender_bidder)
    test_delete_tender_bidder = snitch(delete_tender_bidder)
    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_deleted_bid_do_not_locks_tender_in_state = snitch(deleted_bid_do_not_locks_tender_in_state)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)


class TenderBidDocumentResourceTestMixin(object):
    test_create_tender_bidder_document = snitch(create_tender_bidder_document)
    test_put_tender_bidder_document = snitch(put_tender_bidder_document)
    test_patch_tender_bidder_document = snitch(patch_tender_bidder_document)
    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending)


class TenderBidResourceTest(BaseTenderUAContentWebTest, TenderBidResourceTestMixin):
    initial_data = test_tender_data
    initial_status = 'active.tendering'
    author_data = test_organization

    test_draft1_bid = snitch(draft1_bid)
    test_draft2_bids = snitch(draft2_bids)


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
            self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': [test_organization], "value": {"amount": 500}}})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']

    test_not_found = snitch(not_found)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_create_tender_bidder_document_json = snitch(create_tender_bidder_document_json)
    test_put_tender_bidder_document_json = snitch(put_tender_bidder_document_json)



class TenderBidderBatchDocumentWithDSResourceTest(BaseTenderUAContentWebTest):
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



class TenderBidderBatchDocumentWithDSResourceTest(BaseTenderUAContentWebTest):
    docservice = True
    initial_status = 'active.tendering'

    def test_create_tender_bidder_with_document_invalid(self):
        response = self.app.post_json('/tenders/{}/bids'.format( self.tender_id),
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

        response = self.app.post_json('/tenders/{}/bids'.format( self.tender_id),
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

        response = self.app.post_json('/tenders/{}/bids'.format( self.tender_id),
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

        response = self.app.post_json('/tenders/{}/bids'.format( self.tender_id),
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

        response = self.app.post_json('/tenders/{}/bids'.format( self.tender_id),
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

        response = self.app.post_json('/tenders/{}/bids'.format( self.tender_id),
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

        response = self.app.post_json('/tenders/{}/bids'.format( self.tender_id),
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
        response = self.app.post_json('/tenders/{}/bids'.format( self.tender_id),
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

        response = self.app.post_json('/tenders/{}/bids'.format( self.tender_id),
            {'data': {
                 'tenderers': [test_organization],
                 'value': {'amount': 500},
                 'selfEligible': True,
                 'selfQualified': True,
                 'documents': [{
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
