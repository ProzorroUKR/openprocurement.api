# -*- coding: utf-8 -*-
import unittest
import resource
from nose.plugins.attrib import attr
from datetime import timedelta
from openprocurement.api.models import get_now, SANDBOX_MODE
from openprocurement.api.utils import ROUTE_PREFIX
from openprocurement.api.tests.base import BaseWebTest, test_organization
from openprocurement.tender.openeu.tests.base import BaseTenderWebTest
from openprocurement.tender.competitivedialogue.models import (TenderStage2EU, TenderStage2UA, STAGE_2_UA_TYPE,
                                                               STAGE_2_EU_TYPE, STAGE2_STATUS)
from openprocurement.tender.competitivedialogue.tests.base import (test_tender_data_ua,
                                                                   test_tender_data_eu,
                                                                   BaseCompetitiveDialogEUStage2WebTest,
                                                                   BaseCompetitiveDialogUAStage2WebTest,
                                                                   test_tender_stage2_data_ua,
                                                                   test_tender_stage2_data_eu,
                                                                   test_access_token_stage1
                                                                   )
from copy import deepcopy
from openprocurement.tender.competitivedialogue.models import CD_EU_TYPE, CD_UA_TYPE


class CompetitiveDialogStage2Test(BaseWebTest):
    def test_simple_add_cd__tender_eu(self):
        u = TenderStage2EU(test_tender_stage2_data_eu)
        u.tenderID = "EU-X"

        assert u.id is None
        assert u.rev is None

        u.store(self.db)

        assert u.id is not None
        assert u.rev is not None

        fromdb = self.db.get(u.id)

        assert u.tenderID == fromdb['tenderID']
        assert u.doc_type == "Tender"
        assert u.procurementMethodType == STAGE_2_EU_TYPE

        u.delete_instance(self.db)

    def test_simple_add_cd_tender_ua(self):
        u = TenderStage2UA(test_tender_stage2_data_ua)
        u.tenderID = "UA-X"

        assert u.id is None
        assert u.rev is None

        u.store(self.db)

        assert u.id is not None
        assert u.rev is not None

        fromdb = self.db.get(u.id)

        assert u.tenderID == fromdb['tenderID']
        assert u.doc_type == "Tender"
        assert u.procurementMethodType == STAGE_2_UA_TYPE

        u.delete_instance(self.db)


class CompetitiveDialogStage2EUResourceTest(BaseCompetitiveDialogEUStage2WebTest):

    initial_auth = ('Basic', ('competitive_dialogue', ''))

    def set_tender_status(self, tender, token, status):
        auth = self.app.authorization
        if status == 'draft.stage2':
            self.app.authorization = ('Basic', ('competitive_dialogue', ''))
            response = self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=tender['id'],
                                                                                    token=token),
                                           {'data': {'status': status}})
            self.app.authorization = auth
            return response
        if status == 'active.tendering':
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=tender['id'],
                                                                                    token=token),
                                           {'data': {'status': status}})
            self.app.authorization = auth
            return response

    def test_listing(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        tenders = []
        tokens = []

        for i in range(3):
            offset = get_now().isoformat()
            response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_eu})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            tenders.append(response.json['data'])
            tokens.append(response.json['access']['token'])

        # set status to draft.stage2
        for tender in tenders:
            self.set_tender_status(tender, tokens[tenders.index(tender)], 'draft.stage2')

        # set status to active.tendering
        for tender in tenders:
            offset = get_now().isoformat()
            response = self.set_tender_status(tender, tokens[tenders.index(tender)], 'active.tendering')
            tenders[tenders.index(tender)] = response.json['data']

        ids = ','.join([i['id'] for i in tenders])

        while True:
            response = self.app.get('/tenders')
            self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
            if len(response.json['data']) == 3:
                break

        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
        self.assertEqual(set([i['dateModified'] for i in response.json['data']]),
                         set([i['dateModified'] for i in tenders]))
        self.assertEqual([i['dateModified'] for i in response.json['data']],
                         sorted([i['dateModified'] for i in tenders]))

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
        self.assertEqual([i['dateModified'] for i in response.json['data']],
                         sorted([i['dateModified'] for i in tenders], reverse=True))

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

        test_tender_stage2_data_ua2 = test_tender_stage2_data_eu.copy()
        test_tender_stage2_data_ua2['mode'] = 'test'
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_ua2})
        self.set_tender_status(response.json['data'], response.json['access']['token'], 'draft.stage2')
        self.set_tender_status(response.json['data'], response.json['access']['token'], 'active.tendering')
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        while True:
            response = self.app.get('/tenders?mode=test')
            self.assertEqual(response.status, '200 OK')
            if len(response.json['data']) == 1:
                break
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get('/tenders?mode=_all_')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 4)

    def test_listing_changes(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        response = self.app.get('/tenders?feed=changes')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        tenders = []
        tokens = []

        for i in range(3):
            response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_eu})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            token = response.json['access']['token']
            data = response.json['data']
            self.set_tender_status(data, token, 'draft.stage2')
            data = self.set_tender_status(data, token, 'active.tendering').json['data']
            tenders.append(data)
            tokens.append(token)

        ids = ','.join([i['id'] for i in tenders])

        while True:
            response = self.app.get('/tenders?feed=changes')
            self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
            if len(response.json['data']) == 3:
                break

        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
        self.assertEqual(set([i['dateModified'] for i in response.json['data']]),
                         set([i['dateModified'] for i in tenders]))
        self.assertEqual([i['dateModified'] for i in response.json['data']],
                         sorted([i['dateModified'] for i in tenders]))

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
        self.assertEqual([i['dateModified'] for i in response.json['data']],
                         sorted([i['dateModified'] for i in tenders], reverse=True))

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

        test_tender_stage2_data_ua2 = test_tender_stage2_data_eu.copy()
        test_tender_stage2_data_ua2['mode'] = 'test'
        response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_ua2})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.set_tender_status(response.json['data'], response.json['access']['token'], 'draft.stage2')
        self.set_tender_status(response.json['data'], response.json['access']['token'], 'active.tendering')

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
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        tenders = []
        data = test_tender_stage2_data_eu.copy()
        data.update({'status': 'draft'})

        for i in range(3):
            response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_eu})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            self.set_tender_status(response.json['data'], response.json['access']['token'], 'draft.stage2')
            response = self.set_tender_status(response.json['data'], response.json['access']['token'],
                                              'active.tendering')
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
        self.assertEqual(set([i['dateModified'] for i in response.json['data']]),
                         set([i['dateModified'] for i in tenders]))
        self.assertEqual([i['dateModified'] for i in response.json['data']],
                         sorted([i['dateModified'] for i in tenders]))

    def test_create_tender_invalid(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        request_path = '/tenders'
        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                 u"Content-Type header should be one of ['application/json']", u'location': u'header',
             u'name': u'Content-Type'}
        ])

        response = self.app.post(request_path, 'data', content_type='application/json', status=422)
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

        response = self.app.post_json(request_path, {'not_data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
             u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, {'data': []}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
             u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'invalid_value'}},
                                      status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not implemented', u'location': u'data', u'name': u'procurementMethodType'}
        ])

        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=403)
        self.app.post_json(request_path, {'data': {'value': 'invalid_value'}}, status=403)
        self.app.post_json(request_path, {'data': {'procurementMethod': 'invalid_value'}}, status=403)
        self.app.post_json(request_path, {'data': {'enquiryPeriod': {'endDate': 'invalid_value'}}},
                           status=403)
        self.app.post_json(request_path, {'data': {'enquiryPeriod': {'endDate': '9999-12-31T23:59:59.999999'}}},
                           status=403)

        data = test_tender_stage2_data_ua['tenderPeriod']
        test_tender_stage2_data_ua['tenderPeriod'] = {'startDate': '2014-10-31T00:00:00',
                                                      'endDate': '2014-10-01T00:00:00'}
        response = self.app.post_json(request_path, {'data': test_tender_stage2_data_ua}, status=422)
        test_tender_stage2_data_ua['tenderPeriod'] = data
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'startDate': [u'period should begin before its end']}, u'location': u'body',
             u'name': u'tenderPeriod'}
        ])

        test_tender_stage2_data_ua['tenderPeriod']['startDate'] = (get_now() - timedelta(minutes=30)).isoformat()
        response = self.app.post_json(request_path, {'data': test_tender_stage2_data_ua}, status=422)
        del test_tender_stage2_data_ua['tenderPeriod']['startDate']
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'tenderPeriod.startDate should be in greater than current date'],
             u'location': u'body', u'name': u'tenderPeriod'}
        ])

        now = get_now()
        test_tender_stage2_data_ua['awardPeriod'] = {'startDate': now.isoformat(), 'endDate': now.isoformat()}
        response = self.app.post_json(request_path, {'data': test_tender_stage2_data_ua}, status=422)
        del test_tender_stage2_data_ua['awardPeriod']
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'period should begin after tenderPeriod'], u'location': u'body',
             u'name': u'awardPeriod'}
        ])

        test_tender_stage2_data_ua['auctionPeriod'] = {'startDate': (now + timedelta(days=35)).isoformat(),
                                                       'endDate': (now + timedelta(days=35)).isoformat()}
        test_tender_stage2_data_ua['awardPeriod'] = {'startDate': (now + timedelta(days=34)).isoformat(),
                                                     'endDate': (now + timedelta(days=34)).isoformat()}
        response = self.app.post_json(request_path, {'data': test_tender_stage2_data_ua}, status=422)
        del test_tender_stage2_data_ua['auctionPeriod']
        del test_tender_stage2_data_ua['awardPeriod']
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'period should begin after auctionPeriod'], u'location': u'body',
             u'name': u'awardPeriod'}
        ])

        data = test_tender_stage2_data_ua['minimalStep']
        test_tender_stage2_data_ua['minimalStep'] = {'amount': '6674850281.0'}
        response = self.app.post_json(request_path, {'data': test_tender_stage2_data_ua}, status=422)
        test_tender_stage2_data_ua['minimalStep'] = data
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'value should be less than value of tender'], u'location': u'body',
             u'name': u'minimalStep'}
        ])

        data = test_tender_stage2_data_ua['minimalStep']
        test_tender_stage2_data_ua['minimalStep'] = {'amount': '100.0', 'valueAddedTaxIncluded': False}
        response = self.app.post_json(request_path, {'data': test_tender_stage2_data_ua}, status=422)
        test_tender_stage2_data_ua['minimalStep'] = data
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [
                u'valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of value of tender'],
                u'location': u'body', u'name': u'minimalStep'}
        ])

        data = test_tender_stage2_data_ua['minimalStep']
        test_tender_stage2_data_ua['minimalStep'] = {'amount': '100.0', 'currency': "USD"}
        response = self.app.post_json(request_path, {'data': test_tender_stage2_data_ua}, status=422)
        test_tender_stage2_data_ua['minimalStep'] = data
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'currency should be identical to currency of value of tender'], u'location': u'body',
             u'name': u'minimalStep'}
        ])

        data = test_tender_stage2_data_ua["items"][0]["additionalClassifications"][0]["scheme"]
        test_tender_stage2_data_ua["items"][0]["additionalClassifications"][0]["scheme"] = 'Не ДКПП'
        response = self.app.post_json(request_path, {'data': test_tender_stage2_data_ua}, status=422)
        test_tender_stage2_data_ua["items"][0]["additionalClassifications"][0]["scheme"] = data
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'additionalClassifications': [
                u"One of additional classifications should be one of [ДКПП, NONE, ДК003, ДК015, ДК018]."]}],
                u'location': u'body', u'name': u'items'}
        ])

        data = test_tender_stage2_data_ua["procuringEntity"]["contactPoint"]["telephone"]
        del test_tender_stage2_data_ua["procuringEntity"]["contactPoint"]["telephone"]
        response = self.app.post_json(request_path, {'data': test_tender_stage2_data_ua}, status=422)
        test_tender_stage2_data_ua["procuringEntity"]["contactPoint"]["telephone"] = data
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': {u'email': [u'telephone or email should be present']}},
             u'location': u'body', u'name': u'procuringEntity'}
        ])

        data = test_tender_stage2_data_ua["items"][0].copy()
        classification = data['classification'].copy()
        classification["id"] = u'19212310-1'
        data['classification'] = classification
        test_tender_stage2_data_ua["items"] = [test_tender_stage2_data_ua["items"][0], data]
        response = self.app.post_json(request_path, {'data': test_tender_stage2_data_ua}, status=422)
        test_tender_stage2_data_ua["items"] = test_tender_stage2_data_ua["items"][:1]
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'CPV group of items be identical'], u'location': u'body', u'name': u'items'}
        ])

        data = deepcopy(test_tender_stage2_data_ua)
        del data["items"][0]['deliveryAddress']['postalCode']
        del data["items"][0]['deliveryAddress']['locality']
        del data["items"][0]['deliveryDate']
        response = self.app.post_json(request_path, {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'deliveryDate': [u'This field is required.'],
                               u'deliveryAddress': {u'postalCode': [u'This field is required.'],
                                                    u'locality': [u'This field is required.']}}],
             u'location': u'body', u'name': u'items'}
        ])

    # def test_create_tender_generated(self):
    #     self.app.authorization = ('Basic', ('competitive_dialogue', ''))
    #     data = test_tender_stage2_data_ua.copy()
    #     # del data['awardPeriod']
    #     data.update({'id': 'hash', 'doc_id': 'hash2', 'tenderID': 'hash3'})
    #     response = self.app.post_json('/tenders', {'data': data})
    #     self.assertEqual(response.status, '201 Created')
    #     self.assertEqual(response.content_type, 'application/json')
    #     self.set_tender_status(response.json['data'], response.json['access']['token'], 'draft.stage2')
    #     response = self.set_tender_status(response.json['data'], response.json['access']['token'], 'active.tendering')
    #
    #     tender = response.json['data']
    #     if 'procurementMethodDetails' in tender:
    #         tender.pop('procurementMethodDetails')
    #     self.assertEqual(set(tender), set([
    #         u'procurementMethodType', u'id', u'dateModified', u'tenderID',
    #         u'status', u'enquiryPeriod', u'tenderPeriod',
    #         u'complaintPeriod', u'minimalStep', u'items', u'value', u'owner',
    #         u'procuringEntity', u'next_check', u'procurementMethod',
    #         u'awardCriteria', u'submissionMethod', u'title', u'title_en', u'date', u'description',
    #         u'lots', u'dialogueID', u'description_en', u'shortlistedFirms']))
    #     self.assertNotEqual(data['id'], tender['id'])
    #     self.assertNotEqual(data['doc_id'], tender['id'])
    #     self.assertNotEqual(data['tenderID'], tender['tenderID'])

    def test_create_tender(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)
        response = self.app.post_json('/tenders', {"data": test_tender_stage2_data_eu})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        tender = response.json['data']
        tender_set = set(tender)
        if 'procurementMethodDetails' in tender_set:
            tender_set.remove('procurementMethodDetails')
        self.assertEqual(tender_set - set(self.initial_data), set([
            u'id', u'dateModified', u'enquiryPeriod',
            u'complaintPeriod', u'tenderID',
            u'awardCriteria', u'submissionMethod', u'date'
        ]))
        self.assertIn(tender['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data']), set(tender))
        self.assertEqual(response.json['data'], tender)

        response = self.app.post_json('/tenders?opt_jsonp=callback', {"data": test_tender_stage2_data_eu})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('callback({"', response.body)

        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_stage2_data_eu})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "', response.body)

        response = self.app.post_json('/tenders', {"data": test_tender_stage2_data_eu, "options": {"pretty": True}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "', response.body)

        tender_data = deepcopy(test_tender_stage2_data_eu)
        tender_data['guarantee'] = {"amount": 100500, "currency": "USD"}
        response = self.app.post_json('/tenders', {'data': tender_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        data = response.json['data']
        self.assertIn('guarantee', data)
        self.assertEqual(data['guarantee']['amount'], 100500)
        self.assertEqual(data['guarantee']['currency'], "USD")

    def test_get_tender(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_eu})
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

    def test_tender_features_invalid(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        data = test_tender_stage2_data_eu.copy()
        item = data['items'][0].copy()
        item['id'] = "1"
        data['items'] = [item, item.copy()]
        response = self.app.post_json('/tenders', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Item id should be uniq for all items'], u'location': u'body', u'name': u'items'}
        ])
        data['items'][0]["id"] = "0"
        data['features'] = [
            {
                "code": "OCDS-123454-AIR-INTAKE",
                "featureOf": "lot",
                "title": u"Потужність всмоктування",
                "enum": [
                    {
                        "value": 0.1,
                        "title": u"До 1000 Вт"
                    },
                    {
                        "value": 0.15,
                        "title": u"Більше 1000 Вт"
                    },
                    {
                        "value": 0.3,
                        "title": u"До 500 Вт"
                    }
                ]
            }
        ]
        response = self.app.post_json('/tenders', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedItem': [u'This field is required.']}], u'location': u'body',
             u'name': u'features'}
        ])
        data['features'][0]["relatedItem"] = "2"
        response = self.app.post_json('/tenders', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedItem': [u'relatedItem should be one of lots']}], u'location': u'body',
             u'name': u'features'}
        ])
        data['features'][0]["featureOf"] = "item"
        response = self.app.post_json('/tenders', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedItem': [u'relatedItem should be one of items']}], u'location': u'body',
             u'name': u'features'}
        ])
        data['features'][0]["relatedItem"] = "1"
        data['features'][0]["enum"][0]["value"] = 0.5
        response = self.app.post_json('/tenders', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'enum': [{u'value': [u'Float value should be less than 0.3.']}]}], u'location': u'body',
             u'name': u'features'}
        ])
        data['features'][0]["enum"][0]["value"] = 0.15
        response = self.app.post_json('/tenders', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'enum': [u'Feature value should be uniq for feature']}], u'location': u'body',
             u'name': u'features'}
        ])
        data['features'][0]["enum"][0]["value"] = 0.1
        data['features'].append(data['features'][0].copy())
        response = self.app.post_json('/tenders', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Feature code should be uniq for all features'], u'location': u'body',
             u'name': u'features'}
        ])
        copy_data = deepcopy(data)
        copy_data['features'][1]["code"] = u"OCDS-123454-YEARS"
        copy_data['features'][1]["enum"][0]["value"] = 0.2
        feature = deepcopy(copy_data['features'][1])
        feature["code"] = u"OCDS-123455-YEARS"
        copy_data['features'].append(feature)
        feature = deepcopy(copy_data['features'][1])
        feature["code"] = u"OCDS-123456-YEARS"
        copy_data['features'].append(feature)
        response = self.app.post_json('/tenders', {'data': copy_data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Sum of max value of all features should be less then or equal to 99%'],
             u'location': u'body', u'name': u'features'}
        ])
        del copy_data
        del feature

    def test_tender_features(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        data = test_tender_stage2_data_eu.copy()
        item = data['items'][0].copy()
        item['id'] = "1"
        data['items'] = [item]
        data['features'] = [
            {
                "code": "OCDS-123454-AIR-INTAKE",
                "featureOf": "item",
                "relatedItem": "1",
                "title": u"Потужність всмоктування",
                "title_en": u"Air Intake",
                "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 1000 Вт"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 1000 Вт"
                    }
                ]
            },
            {
                "code": "OCDS-123454-YEARS",
                "featureOf": "tenderer",
                "title": u"Років на ринку",
                "title_en": u"Years trading",
                "description": u"Кількість років, які організація учасник працює на ринку",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 3 років"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 3 років"
                    }
                ]
            },
            {
                "code": "OCDS-123454-POSTPONEMENT",
                "featureOf": "tenderer",
                "title": u"Відстрочка платежу",
                "title_en": u"Postponement of payment",
                "description": u"Термін відстрочки платежу",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 90 днів"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 90 днів"
                    }
                ]
            }
        ]
        response = self.app.post_json('/tenders', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        tender = response.json['data']
        self.assertEqual(tender['features'], data['features'])
        token = response.json['access']['token']
        self.tender_id = response.json['data']['id']
        # switch to draft.stage2
        self.set_status(STAGE2_STATUS)
        response = self.app.get('/tenders/{}?acc_token={}'.format(tender['id'], token))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('features', response.json['data'])

    def test_patch_tender(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_eu})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        self.assertEqual(tender['status'], 'draft')
        self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        dateModified = tender.pop('dateModified')

        self.set_status(STAGE2_STATUS)

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.patch_json('/tenders/{}/credentials?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': ''}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        response = self.app.patch_json('/tenders/{}/credentials?acc_token={}'.format(tender['id'],
                                                                                     test_access_token_stage1),
                                       {'data': ''})
        self.assertEqual(response.status, '200 OK')

        owner_token = response.json['access']['token']

        # switch to active.tendering
        self.set_status('active.tendering')
        tender["status"] = 'active.tendering'

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'tenderPeriod': {"endDate": response.json['data']['tenderPeriod']['endDate']}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'procuringEntity': {'kind': 'defense'}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotEqual(response.json['data']['procuringEntity']['kind'], 'defense')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'items': [test_tender_stage2_data_eu['items'][0]]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'items': [{}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']['items']), 1)

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'items': [{"classification": {
                                           "scheme": "CPV",
                                           "id": "55523100-3",
                                           "description": "Послуги з харчування у школах"
                                       }}]}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'items': [{"additionalClassifications": [
                                           tender['items'][0]["additionalClassifications"][0] for i in range(3)
                                           ]}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {
            'data': {'items': [{"additionalClassifications": tender['items'][0]["additionalClassifications"]}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {"data": {"guarantee": {"valueAddedTaxIncluded": True}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'][0],
                         {u'description': {u'valueAddedTaxIncluded': u'Rogue field'}, u'location': u'body',
                          u'name': u'guarantee'})

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {"data": {"guarantee": {"amount": 12}}})
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('guarantee', response.json['data'])

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {"data": {"guarantee": {"amount": 100, "currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('guarantee', response.json['data'])

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'status': 'active.auction'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update tender in current (complete) status")

    def test_patch_tender_eu(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_eu})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        owner_token = response.json['access']['token']
        dateModified = tender.pop('dateModified')
        self.tender_id = tender['id']
        self.go_to_enquiryPeriod_end()

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {"value": {
                                           "amount": 501,
                                           "currency": u"UAH"
                                       }}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "tenderPeriod should be extended by 7 days")
        tenderPeriod_endDate = get_now() + timedelta(days=7, seconds=10)
        enquiryPeriod_endDate = tenderPeriod_endDate - (
        timedelta(minutes=10) if SANDBOX_MODE else timedelta(days=10))
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data':
            {
                "value": {
                    "amount": 502,
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
        self.assertNotEqual(response.json['data']['value']['amount'], 502)
        self.assertNotEqual(response.json['data']['value']['amount'], 501)

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {"data": {"guarantee": {"valueAddedTaxIncluded": True}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'][0],
                         {u'description': {u'valueAddedTaxIncluded': u'Rogue field'}, u'location': u'body',
                          u'name': u'guarantee'})

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {"data": {"guarantee": {"amount": 12}}})
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('guarantee', response.json['data'])

    def test_dateModified_tender(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        response = self.app.get('/tenders')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_eu})
        self.assertEqual(response.status, '201 Created')

        self.tender_id = response.json['data']['id']
        # switch to active.tendering
        self.set_status('active.tendering')

        tender = response.json['data']
        dateModified = tender['dateModified']
        owner_token = response.json['access']['token']

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['dateModified'], dateModified)

        self.app.authorization = ('Basic', ('broker', ''))


        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'procurementMethodRationale': 'Open'}})
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
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
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

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.patch_json(
            '/tenders/some_id', {'data': {}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

    def test_guarantee(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        data = deepcopy(test_tender_stage2_data_eu)
        data['guarantee'] = {"amount": 55}
        response = self.app.post_json('/tenders', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertIn('guarantee', response.json['data'])
        tender = response.json['data']
        self.tender_id = response.json['data']['id']
        # switch to active.tendering
        self.set_status('active.tendering')

        owner_token = response.json['access']['token']
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'guarantee': {"amount": 70}}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 55)
        self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

    def test_tender_Administrator_change(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_eu})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']

        self.set_tender_status(tender, response.json['access']['token'], 'draft.stage2')
        response = self.set_tender_status(tender, response.json['access']['token'], 'active.tendering')

        tender = response.json['data']

        self.app.authorization = ('Basic', ('broker', ''))
        author = deepcopy(test_organization)
        response = self.app.post_json('/tenders/{}/questions'.format(tender['id']),
                                      {'data': {'title': 'question title', 'description': 'question description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('administrator', ''))
        response = self.app.patch_json('/tenders/{}'.format(tender['id']), {
            'data': {'mode': u'test', 'procuringEntity': {"identifier": {"id": "00000000"}}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['mode'], u'test')
        self.assertEqual(response.json['data']["procuringEntity"]["identifier"]["id"], "00000000")

        response = self.app.patch_json('/tenders/{}/questions/{}'.format(tender['id'], question['id']),
                                       {"data": {"answer": "answer"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [
            {"location": "url", "name": "role", "description": "Forbidden"}
        ])

        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_eu})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender['id'], owner_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        self.app.authorization = ('Basic', ('administrator', ''))
        response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'mode': u'test'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['mode'], u'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
