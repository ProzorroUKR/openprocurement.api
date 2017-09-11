# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.openeu.tests.base import (BaseTenderContentWebTest,
    test_bids, test_lots)


class TenderCancellationResourceTest(BaseTenderContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    def test_create_tender_cancellation_invalid(self):
        response = self.app.post_json('/tenders/some_id/cancellations', {
                                      'data': {'reason': 'cancellation reason'}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token)

        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
        ])

        response = self.app.post(
            request_path, 'data', content_type='application/json', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'No JSON object could be decoded',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, 'data', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(
            request_path, {'not_data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'reason'},
        ])

        response = self.app.post_json(request_path, {'data': {
                                      'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            "cancellationOf": "lot"
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedLot'}
        ])

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            "cancellationOf": "lot",
            "relatedLot": '0' * 32
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedLot should be one of lots'], u'location': u'body', u'name': u'relatedLot'}
        ])

    def test_create_tender_cancellation(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['reasonType'], 'cancelled')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason', 'reasonType': 'unsuccessful', 'status': 'active'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reasonType'], 'unsuccessful')
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation in current (cancelled) tender status")

    def test_patch_tender_cancellation(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation['id'], self.tender_token), {"data": {'reasonType': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["reasonType"], "unsuccessful")

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update cancellation in current (cancelled) tender status")

        response = self.app.patch_json('/tenders/{}/cancellations/some_id?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {"status": "active"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/cancellations/some_id', {"data": {"status": "active"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")

    def test_get_tender_cancellation(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], cancellation)

        response = self.app.get('/tenders/{}/cancellations/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.get('/tenders/some_id/cancellations/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_cancellations(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.get('/tenders/{}/cancellations'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], cancellation)

        response = self.app.get('/tenders/some_id/cancellations', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

class TenderCancellationBidsAvailabilityTest(BaseTenderContentWebTest):
    initial_auth = ('Basic', ('broker', ''))
    initial_bids = test_bids * 2
    bid_visible_fields = [u'status', u'documents', u'tenderers', u'id', u'eligibilityDocuments']
    doc_id_by_type = {}
    valid_bids = []

    def setUp(self):
        super(TenderCancellationBidsAvailabilityTest, self).setUp()
        self.valid_bids = self.initial_bids_tokens.keys()
        self._prepare_bids_docs()

    def test_bids_on_tender_cancellation_in_tendering(self):
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        tender = response.json['data']
        self.assertNotIn('bids', tender)  # bids not visible for others

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason', "status": "active"}})
        self.assertEqual(response.status, '201 Created')
        cancellation = response.json['data']
        self.assertEqual(cancellation["status"], 'active')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        tender = response.json['data']
        self.assertNotIn('bids', tender)
        self.assertEqual(tender["status"], 'cancelled')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'cancelled')

    def _mark_one_bid_deleted(self):
        bid_id, bid_token = self.initial_bids_tokens.items()[0]
        response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, bid_token))
        self.assertEqual(response.status, '200 OK')
        self.valid_bids.remove(bid_id)
        return bid_id

    def _prepare_bids_docs(self):
        doc_id_by_type = {}
        for bid_id, bid_token in self.initial_bids_tokens.items():
            for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
                response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
                    self.tender_id, bid_id, doc_resource, bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
                doc_id = response.json["data"]['id']

                self.assertIn(doc_id, response.headers['Location'])
                self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
                key = response.json["data"]["url"].split('?')[-1]
                doc_id_by_type[bid_id + doc_resource] = {'id': doc_id, 'key': key}

        self.doc_id_by_type = doc_id_by_type

    def _cancel_tender(self):
        orig_authorization = self.app.authorization
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason', "status": "active"}})
        self.assertEqual(response.status, '201 Created')
        cancellation = response.json['data']
        self.assertEqual(cancellation["status"], 'active')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        tender = response.json['data']
        self.assertIn('bids', tender)
        self.assertEqual(tender["status"], 'cancelled')
        self.app.authorization = orig_authorization
        return tender

    def _qualify_bids_and_switch_to_pre_qualification_stand_still(self, qualify_all=True):
        orig_authorization = self.app.authorization
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        qualifications = response.json['data']
        self.assertEqual(len(qualifications), 3)
        offset = 0 if qualify_all else 1
        for qualification in qualifications[offset:]:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        if offset:
            qualification = qualifications[0]
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token), {"data": {"status": "unsuccessful"}})
            self.assertEqual(response.status, "200 OK")
            self.valid_bids.remove(qualification['bidID'])

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')
        self.app.authorization = orig_authorization

    def _all_documents_are_not_accessible(self, bid_id):
        for doc_resource in ['documents', 'eligibility_documents', 'financial_documents', 'qualification_documents']:
            response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, bid_id, doc_resource), status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertIn("Can\'t view bid documents in current (", response.json['errors'][0]["description"])
            response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, bid_id, doc_resource, self.doc_id_by_type[bid_id + doc_resource]['id']), status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertIn("Can\'t view bid documents in current (", response.json['errors'][0]["description"])

    def _check_visible_fields_for_invalidated_bids(self):
        orig_authorization = self.app.authorization
        self.app.authorization = ('Basic', ('broker', ''))

        for bid_id, bid_token in self.initial_bids_tokens.items():
            response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid_id))
            bid_data = response.json['data']
            if bid_id in self.valid_bids:
                self.assertEqual(set(bid_data.keys()), set(self.bid_visible_fields))

                for doc_resource in ['documents', 'eligibility_documents']:
                    response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, bid_id, doc_resource))
                    docs = response.json['data']
                    self.assertEqual(len(docs), 1)
                    self.assertEqual(docs[0]['title'], "name_{}.doc".format(doc_resource[:-1]))
                    self.assertIn('url', docs[0])

                for doc_resource in ['financial_documents', 'qualification_documents']:
                    response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, bid_id, doc_resource), status=403)
                    self.assertEqual(response.status, '403 Forbidden')
                    self.assertEqual(response.json['errors'][0]["description"], "Can\'t view bid documents in current (invalid.pre-qualification) bid status")
                    response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, bid_id, doc_resource, self.doc_id_by_type[bid_id + doc_resource]['id']), status=403)
                    self.assertEqual(response.status, '403 Forbidden')
                    self.assertEqual(response.json['errors'][0]["description"], "Can\'t view bid documents in current (invalid.pre-qualification) bid status")
            else:
                self.assertEqual(set(bid_data.keys()), set(['id', 'status']))
                self._all_documents_are_not_accessible(bid_id)

        self.app.authorization = orig_authorization

    def _set_auction_results(self):
        orig_authorization = self.app.authorization
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.patch_json('/tenders/{}/auction'.format(self.tender_id),
                                       {
                                           'data': {
                                               'auctionUrl': 'https://tender.auction.url',
                                               'bids': [
                                                   {
                                                       'id': i['id'],
                                                       'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                                                   }
                                                   for i in auction_bids_data
                                               ]
                                           }
        })
        response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                      {'data': {'bids': auction_bids_data}})
        self.assertEqual(response.status, "200 OK")
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')
        self.app.authorization = orig_authorization

    def _bid_document_is_accessible(self, bid_id, doc_resource):
        response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, bid_id, doc_resource))
        docs = response.json['data']
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['title'], "name_{}.doc".format(doc_resource[:-1]))
        self.assertIn('url', docs[0])
        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, bid_id, doc_resource, self.doc_id_by_type[bid_id + doc_resource]['id']))
        doc = response.json['data']
        self.assertEqual(doc['title'], "name_{}.doc".format(doc_resource[:-1]))

    def test_bids_on_tender_cancellation_in_pre_qualification(self):
        self._mark_one_bid_deleted()

        # leave one bid invalidated
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {"description": "2 b | !2 b"}})
        for bid_id in self.valid_bids:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, self.initial_bids_tokens[bid_id]))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'invalid')
        invalid_bid_id = self.valid_bids.pop()
        self.assertEqual(len(self.valid_bids), 2)
        for bid_id in self.valid_bids:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, self.initial_bids_tokens[bid_id]), {"data": {
                'status': 'pending',
                }})

        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        tender = self._cancel_tender()

        for bid in tender['bids']:
            if bid['id'] in self.valid_bids:
                self.assertEqual(bid["status"], 'invalid.pre-qualification')
                self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
            elif bid['id'] == invalid_bid_id:
                self.assertEqual(bid["status"], 'invalid')
                self.assertEqual(set(bid.keys()), set(['id', 'status']))
            else:
                self.assertEqual(bid["status"], 'deleted')
                self.assertEqual(set(bid.keys()), set(['id', 'status']))

        self._check_visible_fields_for_invalidated_bids()

    def test_bids_on_tender_cancellation_in_pre_qualification_stand_still(self):
        self._mark_one_bid_deleted()

        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        self._qualify_bids_and_switch_to_pre_qualification_stand_still()

        tender = self._cancel_tender()

        self.app.authorization = ('Basic', ('broker', ''))

        for bid in tender['bids']:
            if bid['id'] in self.valid_bids:
                self.assertEqual(bid["status"], 'invalid.pre-qualification')
                self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
            else:
                self.assertEqual(bid["status"], 'deleted')
                self.assertEqual(set(bid.keys()), set(['id', 'status']))

        self._check_visible_fields_for_invalidated_bids()

    def test_bids_on_tender_cancellation_in_auction(self):
        self._mark_one_bid_deleted()

        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        self._qualify_bids_and_switch_to_pre_qualification_stand_still()

        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        tender = self._cancel_tender()

        self.app.authorization = ('Basic', ('broker', ''))
        for bid in tender['bids']:
            if bid['id'] in self.valid_bids:
                self.assertEqual(bid["status"], 'invalid.pre-qualification')
                self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
            else:
                self.assertEqual(bid["status"], 'deleted')
                self.assertEqual(set(bid.keys()), set(['id', 'status']))
                self._all_documents_are_not_accessible(bid['id'])
        self._check_visible_fields_for_invalidated_bids()

    def test_bids_on_tender_cancellation_in_qualification(self):
        self.bid_visible_fields = [
            u'status', u'documents', u'tenderers', u'id', u'selfQualified',
            u'eligibilityDocuments', u'selfEligible', u'value', u'date',
            u'financialDocuments', u'participationUrl', u'qualificationDocuments'
        ]
        deleted_bid_id = self._mark_one_bid_deleted()

        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        self._qualify_bids_and_switch_to_pre_qualification_stand_still(qualify_all=False)

        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        self._set_auction_results()

        tender = self._cancel_tender()

        self.app.authorization = ('Basic', ('broker', ''))
        for bid in tender['bids']:
            if bid['id'] in self.valid_bids:
                self.assertEqual(bid["status"], 'active')
                self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
            elif bid['id'] == deleted_bid_id:
                self.assertEqual(bid["status"], 'deleted')
                self.assertEqual(set(bid.keys()), set(['id', 'status']))
            else:
                self.assertEqual(bid["status"], 'unsuccessful')
                self.assertEqual(set(bid.keys()), set([
                    u'documents', u'eligibilityDocuments', u'id', u'status',
                    u'selfEligible', u'tenderers', u'selfQualified',
                ]))

        for bid_id, bid_token in self.initial_bids_tokens.items():
            response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid_id))
            bid_data = response.json['data']

            if bid_id in self.valid_bids:
                self.assertEqual(set(bid_data.keys()), set(self.bid_visible_fields))

                for doc_resource in ['documents', 'eligibility_documents', 'financial_documents', 'qualification_documents']:
                    self._bid_document_is_accessible(bid_id, doc_resource)
            elif bid_id == deleted_bid_id:
                self._all_documents_are_not_accessible(bid_id)
            else:  # unsuccessful bid
                for doc_resource in ['financial_documents', 'qualification_documents']:
                    response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, bid_id, doc_resource), status=403)
                    self.assertEqual(response.status, '403 Forbidden')
                    self.assertIn("Can\'t view bid documents in current (", response.json['errors'][0]["description"])
                    response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, bid_id, doc_resource, self.doc_id_by_type[bid_id + doc_resource]['id']), status=403)
                    self.assertEqual(response.status, '403 Forbidden')
                    self.assertIn("Can\'t view bid documents in current (", response.json['errors'][0]["description"])
                for doc_resource in ['documents', 'eligibility_documents']:
                    self._bid_document_is_accessible(bid_id, doc_resource)

    def test_bids_on_tender_cancellation_in_awarded(self):
        self.bid_visible_fields = [
            u'status', u'documents', u'tenderers', u'id', u'selfQualified',
            u'eligibilityDocuments', u'selfEligible', u'value', u'date',
            u'financialDocuments', u'participationUrl', u'qualificationDocuments'
        ]
        self._mark_one_bid_deleted()

        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        self._qualify_bids_and_switch_to_pre_qualification_stand_still()

        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        self._set_auction_results()

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")

        response = self.app.get('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.awarded')

        tender = self._cancel_tender()

        self.app.authorization = ('Basic', ('broker', ''))
        for bid in tender['bids']:
            if bid['id'] in self.valid_bids:
                self.assertEqual(bid["status"], 'active')
                self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
            else:
                self.assertEqual(bid["status"], 'deleted')
                self.assertEqual(set(bid.keys()), set(['id', 'status']))

        for bid_id, bid_token in self.initial_bids_tokens.items():

            response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid_id))
            bid_data = response.json['data']
            if bid_id in self.valid_bids:
                self.assertEqual(set(bid_data.keys()), set(self.bid_visible_fields))

                for doc_resource in ['documents', 'eligibility_documents', 'financial_documents', 'qualification_documents']:
                    self._bid_document_is_accessible(bid_id, doc_resource)

class TenderLotCancellationResourceTest(BaseTenderContentWebTest):
    initial_lots = test_lots

    ininitial_auth = ('Basic', ('broker', ''))
    def test_create_tender_cancellation(self):
        lot_id = self.initial_lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            "cancellationOf": "lot",
            "relatedLot": lot_id
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": lot_id
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation in current (cancelled) tender status")

    def test_patch_tender_cancellation(self):
        lot_id = self.initial_lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            "cancellationOf": "lot",
            "relatedLot": lot_id
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update cancellation in current (cancelled) tender status")

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")


class TenderLotsCancellationResourceTest(BaseTenderContentWebTest):
    initial_lots = 2 * test_lots

    initial_auth = ('Basic', ('broker', ''))
    def test_create_tender_cancellation(self):
        lot_id = self.initial_lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            "cancellationOf": "lot",
            "relatedLot": lot_id
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": lot_id
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertNotEqual(response.json['data']["status"], 'cancelled')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": lot_id
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add cancellation only in active lot status")

    def test_patch_tender_cancellation(self):
        lot_id = self.initial_lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            "cancellationOf": "lot",
            "relatedLot": lot_id
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertNotEqual(response.json['data']["status"], 'cancelled')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update cancellation only in active lot status")

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")


class TenderAwardsCancellationResourceTest(BaseTenderContentWebTest):
    initial_lots = 2 * test_lots
    initial_status = 'active.tendering'
    initial_bids = test_bids

    def test_cancellation_active_tendering_j708(self):
        bid = test_bids[0].copy()
        value = bid.pop('value')
        bid['lotValues'] = [
            {
                'value': value,
                'relatedLot': self.initial_lots[0]['id'],
            }
        ]
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid})
        self.assertEqual(response.status, '201 Created')
        self.initial_bids_tokens[response.json['data']['id']] = response.json['access']['token']
        self.initial_bids.append(response.json['data'])

        response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, response.json['data']['id'], response.json['access']['token']))
        self.assertEqual(response.status, '200 OK')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'pending',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]['id']
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, response.json['data']['id'], self.tender_token), {'data': {
            'status': 'active',
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid})
        self.assertEqual(response.status, '201 Created')
        self.initial_bids_tokens[response.json['data']['id']] = response.json['access']['token']
        self.initial_bids.append(response.json['data'])

        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    def test_cancellation_active_qualification(self):
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        qualification_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification_id, self.tender_token),
                                       {"data": {"status": "active", "qualified": True, "eligible": True}})

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]['id']
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

    def test_cancellation_unsuccessful_qualification(self):
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        qualification_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification_id, self.tender_token),
                                       {"data": {"status": "unsuccessful", "qualified": True, "eligible": True}})

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        qualification_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification_id, self.tender_token),
                                       {"data": {"status": "unsuccessful", "qualified": True, "eligible": True}})

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]['id']
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation if all qualifications is unsuccessful")

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation if all qualifications is unsuccessful")

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[1]['id']
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

    def test_cancellation_active_award(self):
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('token', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.auction")

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.initial_lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], "active.qualification")

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                                       {"data": {"status": "active", "qualified": True, "eligible": True}})

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]['id']
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

    def test_cancellation_unsuccessful_award(self):
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('token', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.auction")

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.initial_lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], "active.qualification")

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                                       {"data": {"status": "unsuccessful"}})

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                                       {"data": {"status": "unsuccessful"}})

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]['id']
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation if all awards is unsuccessful")

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation if all awards is unsuccessful")

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[1]['id']
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])


class TenderCancellationDocumentResourceTest(BaseTenderContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']

    def test_not_found(self):
        response = self.app.post('/tenders/some_id/cancellations/some_id/documents', status=404, upload_files=[
                                 ('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post('/tenders/{}/cancellations/some_id/documents'.format(self.tender_id), status=404, upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id, self.cancellation_id, self.tender_token), status=404, upload_files=[
                                 ('invalid_value', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.get('/tenders/some_id/cancellations/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/some_id/documents'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.get('/tenders/some_id/cancellations/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/some_id/documents/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/some_id'.format(self.tender_id, self.cancellation_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        response = self.app.put('/tenders/some_id/cancellations/some_id/documents/some_id', status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.put('/tenders/{}/cancellations/some_id/documents/some_id'.format(self.tender_id), status=404, upload_files=[
                                ('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/some_id'.format(
            self.tender_id, self.cancellation_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_cancellation_document(self):
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
            self.tender_id, self.cancellation_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/cancellations/{}/documents'.format(self.tender_id, self.cancellation_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/cancellations/{}/documents?all=true'.format(self.tender_id, self.cancellation_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?download=some_id'.format(
            self.tender_id, self.cancellation_id, doc_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(
            self.tender_id, self.cancellation_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(
            self.tender_id, self.cancellation_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        self.set_status('complete')

        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
            self.tender_id, self.cancellation_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) tender status")

    def test_put_tender_cancellation_document(self):
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
            self.tender_id, self.cancellation_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id, self.cancellation_id, doc_id, self.tender_token),
                                status=404,
                                upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token), upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(
            self.tender_id, self.cancellation_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(
            self.tender_id, self.cancellation_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token), 'content3', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(
            self.tender_id, self.cancellation_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        self.set_status('complete')

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")

    def test_patch_tender_cancellation_document(self):
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
            self.tender_id, self.cancellation_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id, self.cancellation_id, doc_id, self.tender_token), {"data": {"description": "document description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(
            self.tender_id, self.cancellation_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id, self.cancellation_id, doc_id, self.tender_token), {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

