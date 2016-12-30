import os.path
from jsonpointer import resolve_pointer
from openprocurement.historical.core.utils import HEADER
from openprocurement.api.tests.base import (
    BaseTenderWebTest,
    test_tender_data,
    test_organization,
    test_bids
)
from .base import (
    BaseTenderHistoryWebTest,
    public_revisions
)


class HistoricalTenderTestCase(BaseTenderHistoryWebTest):

    def test_get_tender_invalid_header(self):
        for header in ['invalid', '1.5', '-1']:
            response = self.app.get('/tenders/{}/historical'.format(self.tender_id),
                                    headers={HEADER: header}, status=404)
            self.assertEqual(response.status, '404 Not Found')
            self.assertEqual(response.json['status'], 'error')
            self.assertEqual(response.json['errors'], [
                {u'description': u'Not Found', u'location': u'header', u'name': u'version'}
            ])

    def test_get_tender(self):
        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertIn(HEADER, response.headers)
        self.assertEqual(response.headers[HEADER], str(len(public_revisions)))

    def test_appy_tender_patch(self):
        for ver, rev in list(enumerate(public_revisions))[1:]:
            response = self.app.get('/tenders/{}/historical'.format(self.tender_id),
                                    headers={HEADER: str(ver)})
            self.assertEqual(response.headers[HEADER], str(ver))

            body = response.json['data']
            self.assertEqual(body['dateModified'],
                             public_revisions[int(ver) - 1]['date'])
            self.assertEqual(public_revisions[int(response.headers[HEADER])], rev)
            for p in rev['changes']:
                if not any([v in p['path'] for v in ['shouldStartAfter', 'next_check']]):
                    val = p['value'] if p['op'] != 'remove' else 'missing'
                    self.assertEqual(resolve_pointer(body, p['path'], 'missing'), val)

    def test_get_histoical_tender(self):
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders')
        self.assertEqual(response.json['data'], [])
        response = self.app.post_json('/tenders',
                                      {"data": test_tender_data})
        tender_1 = response.json['data']
        tender_id = self.tender_id = tender_1['id']
        owner_token = response.json['access']['token']

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertNotIn(HEADER, response.headers)
        prev_tender = response.json['data']

        self.change_status_patched('active.tendering')

        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        tender = response.json['data']
        self.assertEqual(response.headers[HEADER], '2')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        tender_2 = response.json['data']
        self.assertEqual(tender, tender_2)

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'tenderers': [test_organization],
                                                "value": {"amount": 500}}})


        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual(response.headers[HEADER], '2')

        self.change_status_patched('active.auction', {'status': 'active.tendering'})
        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual(response.headers[HEADER], '3')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        tender_3 = response.json['data']

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual(response.headers[HEADER], '4')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        tender_4 = response.json['data']

        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        tender = self.db.get(tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token), {"data": {"status": "active"}})
        tender = self.db.get(tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)


        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual(response.headers[HEADER], '5')

        response = self.app.get('/tenders/{}'.format(tender_id))
        tender_5 = response.json['data']
        contract_id = response.json['data']['contracts'][-1]['id']

        self.app.authorization = ('Basic', ('chronograph', ''))
        self.change_status_patched('complete', {'status': 'active.awarded'})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(tender_id))
        tender_6 = response.json['data']

        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token), {"data": {"status": "active"}})
        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual(response.headers[HEADER], '7')

        response = self.app.get('/tenders/{}'.format(tender_id))
        tender_7 = response.json['data']
        for i in ['1', '2', '3', '4', '5', '6', '7']:
            response = self.app.get('/tenders/{}/historical'.format(self.tender_id), headers={HEADER: i})
            tender = locals().get('tender_{}'.format(i))
            for k, v in response.json['data'].items():
                if k not in ['dateModified', 'awards']:
                    self.assertEqual(tender.get(k), v)


class TenderHistoricalAwardTestCase(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def test_historical_award_change(self):
        request_path = '/tenders/{}/awards'.format(self.tender_id)
        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        self.assertEqual(response.status, '201 Created')
        award_1 = response.json['data']

        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual('2', response.headers[HEADER])

        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award_1['id']),
                                       {"data": {"title": "title_1", "description": "description_1"}})
        award_2 = response.json['data']

        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))

        self.assertEqual('3', response.headers[HEADER])
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award_1['id']),
                                       {"data": {"status": "unsuccessful"}})
        award_3 = response.json['data']
        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual('4', response.headers[HEADER])
        for version, award in zip(['2', '3', '4'], [award_1, award_2, award_3]):
            response = self.app.get('/tenders/{}/historical'.format(self.tender_id),
                                    headers={HEADER: version})
            tender = response.json['data']
            self.assertEqual(award, tender.get('awards')[0])


class TenderHistoricalDocumentTestCase(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)

    def test_historical_document_change(self):
        response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json, {"data": []})

        response = self.app.post('/tenders/{}/documents'.format(
            self.tender_id), upload_files=[('file', u'test.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        doc_1 = response.json['data']
        doc_id = doc_1['id']
        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual('2', response.headers[HEADER])

        response = self.app.patch_json('/tenders/{}/documents/{}'.format(self.tender_id, doc_id), {"data": {
            "description": "document description",
            "documentType": 'tenderNotice'
        }})

        self.assertEqual(response.status, '200 OK')
        doc_2 = response.json['data']
        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual('3', response.headers[HEADER])


        response = self.app.patch_json('/tenders/{}/documents/{}'.format(self.tender_id, doc_id), {"data": {
            "documentType": None
        }})
        self.assertEqual(response.status, '200 OK')
        doc_3 = response.json['data']
        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual('4', response.headers[HEADER])
        for version, doc in zip(['2', '3', '4'], [doc_1, doc_2, doc_3]):
            response = self.app.get('/tenders/{}/historical'.format(self.tender_id),
                                    headers={HEADER: version})
            tender = response.json['data']
            self.assertEqual(doc, 
                             tender.get('documents')[0])


class TenderHistoricalDocumentTestCase(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(TenderHistoricalDocumentTestCase, self).setUp()
        # Create award
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id'], 'value': test_tender_data["value"], 'items': test_tender_data["items"]}})
        award = response.json['data']
        self.award_id = award['id']
        self.award_value = award['value']
        self.award_suppliers = award['suppliers']
        self.award_items = award['items']
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {"data": {"status": "active"}})

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        self.set_status('complete', {'status': 'active.awarded'})

    def test_historical_contract_change(self):
        response = self.app.post_json('/tenders/{}/contracts'.format(
            self.tender_id), {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id, 'value': self.award_value, 'suppliers': self.award_suppliers}})
        self.assertEqual(response.status, '201 Created')
        contract_1 = response.json['data']

        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual('4', response.headers[HEADER])

        response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract_1['id']),
                                       {"data": {"value": {"amount": 238}}})
        self.assertEqual(response.status, '200 OK')
        contract_2 = response.json['data']

        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual('5', response.headers[HEADER])

        response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract_1['id']),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        contract_3 = response.json['data']
        response = self.app.get('/tenders/{}/historical'.format(self.tender_id))
        self.assertEqual('6', response.headers[HEADER])
        for i, contract in zip(['4', '5', '6'], [contract_1, contract_2, contract_3]):
            response = self.app.get('/tenders/{}/historical'.format(self.tender_id),
                                    headers={HEADER: i})
            self.assertEqual(contract, response.json['data'].get('contracts')[1])
