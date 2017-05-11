# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from datetime import datetime, timedelta
from openprocurement.api import ROUTE_PREFIX
from openprocurement.api.models import get_now, SANDBOX_MODE
from openprocurement.tender.openua.models import TENDER_PERIOD
from openprocurement.tender.openeu.models import TENDERING_DAYS
from openprocurement.tender.esco.tests.base import (
    test_tender_ua_data, test_tender_eu_data,
    test_organization,
    BaseESCOWebTest, BaseESCOUAContentWebTest, BaseESCOEUContentWebTest,
)
from openprocurement.tender.esco.models import (
    TenderESCOEU, TenderESCOUA
)


class TenderESCOUATest(BaseESCOWebTest):

    initial_auth = ('Basic', ('broker', ''))
    def test_simple_add_tender(self):
        u = TenderESCOUA(test_tender_ua_data)
        u.tenderID = "UA-X"

        assert u.id is None
        assert u.rev is None

        u.store(self.db)

        assert u.id is not None
        assert u.rev is not None

        fromdb = self.db.get(u.id)

        assert u.tenderID == fromdb['tenderID']
        assert u.doc_type == "Tender"
        assert u.procurementMethodType == "esco.UA"
        assert fromdb['procurementMethodType'] == "esco.UA"

        u.delete_instance(self.db)


class TenderESCOEUTest(BaseESCOWebTest):
    initial_auth = ('Basic', ('broker', ''))
    def test_simple_add_tender(self):
        u = TenderESCOEU(test_tender_eu_data)
        u.tenderID = "UA-X"

        assert u.id is None
        assert u.rev is None

        u.store(self.db)

        assert u.id is not None
        assert u.rev is not None

        fromdb = self.db.get(u.id)

        assert u.tenderID == fromdb['tenderID']
        assert u.doc_type == "Tender"
        assert u.procurementMethodType == "esco.EU"
        assert fromdb['procurementMethodType'] == "esco.EU"

        u.delete_instance(self.db)


class TenderESCOTestCommon():

    def test_empty_listing(self):
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertNotIn('{\n    "', response.body)
        self.assertNotIn('callback({', response.body)
        self.assertEqual(response.json['next_page']['offset'], '')
        self.assertNotIn('prev_page', response.json)

        response = self.app.get('/tenders?opt_jsonp=callback')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertNotIn('{\n    "', response.body)
        self.assertIn('callback({', response.body)

        response = self.app.get('/tenders?opt_pretty=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "', response.body)
        self.assertNotIn('callback({', response.body)

        response = self.app.get('/tenders?opt_jsonp=callback&opt_pretty=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('{\n    "', response.body)
        self.assertIn('callback({', response.body)

        response = self.app.get('/tenders?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertIn('descending=1', response.json['next_page']['uri'])
        self.assertIn('limit=10', response.json['next_page']['uri'])
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertIn('limit=10', response.json['prev_page']['uri'])

        response = self.app.get('/tenders?feed=changes')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertEqual(response.json['next_page']['offset'], '')
        self.assertNotIn('prev_page', response.json)

        response = self.app.get('/tenders?feed=changes&offset=0', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Offset expired/invalid', u'location': u'params', u'name': u'offset'}
        ])

        response = self.app.get('/tenders?feed=changes&descending=1&limit=10')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertIn('descending=1', response.json['next_page']['uri'])
        self.assertIn('limit=10', response.json['next_page']['uri'])
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertIn('limit=10', response.json['prev_page']['uri'])

    def test_listing(self):
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        tenders = []

        for i in range(3):
            offset = get_now().isoformat()
            response = self.app.post_json('/tenders', {'data': self.initial_data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            tenders.append(response.json['data'])

        ids = ','.join([i['id'] for i in tenders])

        while True:
            response = self.app.get('/tenders')
            self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
            if len(response.json['data']) == 3:
                break

        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
        self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in tenders]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in tenders]))

        while True:
            response = self.app.get('/tenders?offset={}'.format(offset))
            self.assertEqual(response.status, '200 OK')
            if len(response.json['data']) == 1:
                break
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get('/tenders?limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('prev_page', response.json)
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.get('/tenders', params=[('opt_fields', 'status')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
        self.assertIn('opt_fields=status', response.json['next_page']['uri'])

        response = self.app.get('/tenders', params=[('opt_fields', 'status,enquiryPeriod')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status', u'enquiryPeriod']))
        self.assertIn('opt_fields=status%2CenquiryPeriod', response.json['next_page']['uri'])

        response = self.app.get('/tenders?descending=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in tenders], reverse=True))

        response = self.app.get('/tenders?descending=1&limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        self.initial_data2 = self.initial_data.copy()
        self.initial_data2['mode'] = 'test'
        response = self.app.post_json('/tenders', {'data': self.initial_data2})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        while True:
            response = self.app.get('/tenders?mode=test')
            self.assertEqual(response.status, '200 OK')
            if len(response.json['data']) == 1:
                break
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get('/tenders?mode=_all_')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 4)

    def test_listing_changes(self):
        response = self.app.get('/tenders?feed=changes')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        tenders = []

        for i in range(3):
            response = self.app.post_json('/tenders', {'data': self.initial_data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            tenders.append(response.json['data'])

        ids = ','.join([i['id'] for i in tenders])

        while True:
            response = self.app.get('/tenders?feed=changes')
            self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
            if len(response.json['data']) == 3:
                break

        self.assertEqual(','.join([i['id'] for i in response.json['data']]), ids)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
        self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in tenders]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in tenders]))

        response = self.app.get('/tenders?feed=changes&limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('prev_page', response.json)
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.get('/tenders?feed=changes', params=[('opt_fields', 'status')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
        self.assertIn('opt_fields=status', response.json['next_page']['uri'])

        response = self.app.get('/tenders?feed=changes', params=[('opt_fields', 'status,enquiryPeriod')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status', u'enquiryPeriod']))
        self.assertIn('opt_fields=status%2CenquiryPeriod', response.json['next_page']['uri'])

        response = self.app.get('/tenders?feed=changes&descending=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in tenders], reverse=True))

        response = self.app.get('/tenders?feed=changes&descending=1&limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        self.initial_data2 = self.initial_data.copy()
        self.initial_data2['mode'] = 'test'
        response = self.app.post_json('/tenders', {'data': self.initial_data2})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        while True:
            response = self.app.get('/tenders?feed=changes&mode=test')
            self.assertEqual(response.status, '200 OK')
            if len(response.json['data']) == 1:
                break
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get('/tenders?feed=changes&mode=_all_')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 4)

    def test_listing_draft(self):
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        tenders = []
        data = self.initial_data.copy()
        data.update({'status': 'draft'})

        for i in range(3):
            response = self.app.post_json('/tenders', {'data': self.initial_data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            tenders.append(response.json['data'])
            response = self.app.post_json('/tenders', {'data': data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')

        ids = ','.join([i['id'] for i in tenders])

        while True:
            response = self.app.get('/tenders')
            self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
            if len(response.json['data']) == 3:
                break

        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
        self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in tenders]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in tenders]))

    def test_create_tender(self):
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/tenders', {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        tender = response.json['data']
        tender_set = set(tender)
        if 'procurementMethodDetails' in tender_set:
            tender_set.remove('procurementMethodDetails')
        self.assertEqual(tender_set - set(self.initial_data), set([
            u'id', u'dateModified', u'enquiryPeriod', u'auctionPeriod',
            u'complaintPeriod', u'tenderID', u'status', u'procurementMethod',
            u'awardCriteria', u'submissionMethod', u'next_check', u'owner', u'date',
        ]))
        self.assertIn(tender['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data']), set(tender))
        self.assertEqual(response.json['data'], tender)

        response = self.app.post_json('/tenders?opt_jsonp=callback', {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('callback({"', response.body)

        response = self.app.post_json('/tenders?opt_pretty=1', {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "', response.body)

        response = self.app.post_json('/tenders', {"data": self.initial_data, "options": {"pretty": True}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "', response.body)

        tender_data = deepcopy(self.initial_data)
        tender_data['guarantee'] = {"amount": 100500, "currency": "USD"}
        response = self.app.post_json('/tenders', {'data': tender_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        data = response.json['data']
        self.assertIn('guarantee', data)
        self.assertEqual(data['guarantee']['amount'], 100500)
        self.assertEqual(data['guarantee']['currency'], "USD")

    def test_get_tender(self):
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/tenders', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], tender)

        response = self.app.get('/tenders/{}?opt_jsonp=callback'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('callback({"data": {"', response.body)

        response = self.app.get('/tenders/{}?opt_pretty=1'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "data": {\n        "', response.body)

    def test_patch_tender(self):
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/tenders', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        first_date = tender['date']
        self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        dateModified = tender.pop('dateModified')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['date'], first_date)
        self.assertNotEqual(response.json['data']['status'], 'cancelled')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            tender['id'], owner_token), {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotEqual(response.json['data']['status'], 'cancelled')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'procuringEntity': {'kind': 'defense'}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotEqual(response.json['data']['procuringEntity']['kind'], 'defense')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
            {'data': {'tenderPeriod': {'startDate': tender['enquiryPeriod']['endDate']}}},
            status=422
        )
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [{
                "location": "body",
                "name": "tenderPeriod",
                "description": [
                    "tenderPeriod should be greater than {} days".format(self.tender_period_duration)
                ]
            }
        ])

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            tender['id'], owner_token), {'data': {'procurementMethodRationale': 'Open'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('invalidationDate', response.json['data']['enquiryPeriod'])
        new_tender = response.json['data']
        new_enquiryPeriod = new_tender.pop('enquiryPeriod')
        new_dateModified = new_tender.pop('dateModified')
        tender.pop('enquiryPeriod')
        tender['procurementMethodRationale'] = 'Open'
        self.assertEqual(tender, new_tender)
        self.assertNotEqual(dateModified, new_dateModified)

        revisions = self.db.get(tender['id']).get('revisions')
        self.assertTrue(any([i for i in revisions[-1][u'changes'] if i['op'] == u'remove' and i['path'] == u'/procurementMethodRationale']))

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            tender['id'], owner_token), {'data': {'dateModified': new_dateModified}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        new_tender2 = response.json['data']
        new_enquiryPeriod2 = new_tender2.pop('enquiryPeriod')
        new_dateModified2 = new_tender2.pop('dateModified')
        self.assertEqual(new_tender, new_tender2)
        self.assertNotEqual(new_enquiryPeriod, new_enquiryPeriod2)
        self.assertNotEqual(new_dateModified, new_dateModified2)

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            tender['id'], owner_token), {'data': {'items': [self.initial_data['items'][0]]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            tender['id'], owner_token), {'data': {'items': [{}, self.initial_data['items'][0]]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        item0 = response.json['data']['items'][0]
        item1 = response.json['data']['items'][1]
        self.assertNotEqual(item0.pop('id'), item1.pop('id'))
        self.assertEqual(item0, item1)

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            tender['id'], owner_token), {'data': {'items': [{}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']['items']), 1)

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'items': [{"classification": {
            "scheme": "CPV",
            "id": "44620000-2",
            "description": "Cartons 2"
        }}]}}, status=200)

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'items': [{"classification": {
            "scheme": "CPV",
            "id": "55523100-3",
            "description": "Послуги з харчування у школах"
        }}]}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't change classification")


        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'items': [{"additionalClassifications": [
            tender['items'][0]["additionalClassifications"][0] for i in range(3)
        ]}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'items': [{"additionalClassifications": tender['items'][0]["additionalClassifications"]}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            tender['id'], owner_token), {'data': {'enquiryPeriod': {'endDate': new_dateModified2}}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't change enquiryPeriod")

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'status': 'active.auction'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update tender in current (complete) status")

    def test_dateModified_tender(self):
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/tenders', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        owner_token = response.json['access']['token']
        dateModified = tender['dateModified']

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['dateModified'], dateModified)

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            tender['id'], owner_token), {'data': {'procurementMethodRationale': 'Open'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotEqual(response.json['data']['dateModified'], dateModified)
        tender = response.json['data']
        dateModified = tender['dateModified']

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], tender)
        self.assertEqual(response.json['data']['dateModified'], dateModified)

    def test_tender_not_found(self):
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.get('/tenders/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        response = self.app.patch_json(
            '/tenders/some_id', {'data': {}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

    def test_guarantee(self):
        response = self.app.post_json('/tenders', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertNotIn('guarantee', response.json['data'])
        tender = response.json['data']
        owner_token = response.json['access']['token']
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'guarantee': {"amount": 55}}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 55)
        self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'guarantee': {"amount": 100500, "currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 100500)
        self.assertEqual(response.json['data']['guarantee']['currency'], 'USD')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'guarantee': None}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 100500)
        self.assertEqual(response.json['data']['guarantee']['currency'], 'USD')

        data = deepcopy(self.initial_data)
        data['guarantee'] = {"amount": 100, "currency": "USD"}
        response = self.app.post_json('/tenders', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 100)
        self.assertEqual(response.json['data']['guarantee']['currency'], 'USD')

    def test_tender_Administrator_change(self):
        response = self.app.post_json('/tenders', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']

        response = self.app.post_json('/tenders/{}/questions'.format(tender['id']), {'data': {'title': 'question title', 'description': 'question description', 'author': test_organization}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('administrator', ''))
        response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'mode': u'test', 'procuringEntity': {"identifier":{"id": "00000000"}}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['mode'], u'test')
        self.assertEqual(response.json['data']["procuringEntity"]["identifier"]["id"], "00000000")

        response = self.app.patch_json('/tenders/{}/questions/{}'.format(tender['id'], question['id']), {"data": {"answer": "answer"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [
            {"location": "url", "name": "role", "description": "Forbidden"}
        ])
        self.app.authorization = authorization

        response = self.app.post_json('/tenders', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        owner = response.json['access']['token']

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            tender['id'], owner), {'data': {'reason': 'cancellation reason', 'status': 'active'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        self.app.authorization = ('Basic', ('administrator', ''))
        response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'mode': u'test'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['mode'], u'test')


class TestTenderUA(TenderESCOTestCommon, BaseESCOUAContentWebTest):
    """ ESCO UA tender test """
    initialize_initial_data = False
    initial_data = test_tender_ua_data
    tender_period_duration = TENDER_PERIOD.days

    def test_patch_tender_ua(self):
        response = self.app.post_json('/tenders', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        owner_token = response.json['access']['token']
        dateModified = tender.pop('dateModified')
        self.tender_id = tender['id']
        self.go_to_enquiryPeriod_end()
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {"value": {
            "amount": 501,
            "currency": u"UAH"
        }}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "tenderPeriod should be extended by 7 days")
        tenderPeriod_endDate = get_now() + timedelta(days=7, seconds=10)
        enquiryPeriod_endDate = tenderPeriod_endDate - (timedelta(minutes=10) if SANDBOX_MODE else timedelta(days=10))
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data':
            {
                "value": {
                    "amount": 501,
                    "currency": u"UAH"
                },
                "tenderPeriod": {
                    "endDate": tenderPeriod_endDate.isoformat()
                }
            }
        })
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['tenderPeriod']['endDate'], tenderPeriod_endDate.isoformat())
        self.assertEqual(response.json['data']['enquiryPeriod']['endDate'], enquiryPeriod_endDate.isoformat())

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"guarantee": {"valueAddedTaxIncluded": True}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'][0], {u'description': {u'valueAddedTaxIncluded': u'Rogue field'}, u'location': u'body', u'name': u'guarantee'})

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"guarantee": {"amount": 12}}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 12)
        self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"guarantee": {"currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['guarantee']['currency'], 'USD')


class TestTenderEU(TenderESCOTestCommon, BaseESCOEUContentWebTest):
    """ ESCO EU tender test """
    initialize_initial_data = False
    initial_data = test_tender_eu_data
    tender_period_duration = TENDERING_DAYS
