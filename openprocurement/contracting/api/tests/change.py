# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from openprocurement.api.models import get_now
from openprocurement.contracting.api.tests.base import (
    BaseWebTest, BaseContractContentWebTest, test_contract_data)


class ContractNoItemsChangeTest(BaseWebTest):

    def test_no_items_contract_change(self):
        data = deepcopy(test_contract_data)
        del data['items']
        response = self.app.post_json('/contracts', {"data": data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        contract = response.json['data']
        self.assertEqual(contract['status'], 'active')
        self.assertNotIn('items', contract)
        tender_token = data['tender_token']

        response = self.app.patch_json('/contracts/{}/credentials?acc_token={}'.format(contract['id'], tender_token),
                                       {'data': ''})
        self.assertEqual(response.status, '200 OK')
        token = response.json['access']['token']

        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(contract['id'], token),
                                      {'data': {'rationale': u'причина зміни укр',
                                                'rationaleTypes': ['qualityImprovement']}})
        self.assertEqual(response.status, '201 Created')
        change = response.json['data']
        self.assertEqual(change['status'], 'pending')

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(contract['id'], change['id'], token),
                                       {'data': {'status': 'active'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(contract['id'], token),
                                       {"data": {"status": "terminated", "amountPaid": {"amount": 100, "valueAddedTaxIncluded": True, "currency": "UAH"}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'terminated')

        response = self.app.get('/contracts/{}'.format(contract['id']))
        self.assertNotIn('items', response.json['data'])


class ContractChangesResourceTest(BaseContractContentWebTest):
    initial_auth = ('Basic', ('broker', ''))

    def test_not_found(self):
        response = self.app.get('/contracts/some_id/changes', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'contract_id'}
        ])

        response = self.app.get('/contracts/{}/changes'.format(self.contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.get('/contracts/{}/changes/some_id'.format(self.contract['id']), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'change_id'}
        ])

        response = self.app.patch_json(
            '/contracts/{}/changes/some_id'.format(self.contract['id']), {'data': {}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'change_id'}
        ])

    def test_get_change(self):
        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      {'data': {'rationale': u'Принцеси не какають.',
                                                'rationale_ru': u'ff',
                                                'rationale_en': 'asdf',
                                                'contractNumber': 12,
                                                'rationaleTypes': ['priceReduction']}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        change = response.json['data']
        self.assertEqual(change['status'], 'pending')
        self.assertIn('date', change)

        response = self.app.get('/contracts/{}/changes'.format(self.contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get('/contracts/{}/changes/{}'.format(self.contract['id'], change['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        change_data = response.json['data']
        self.assertEqual(change_data, change)

        response = self.app.get('/contracts/{}'.format(self.contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('changes', response.json['data'])
        self.assertEqual(len(response.json['data']['changes']), 1)
        self.assertEqual(set(response.json['data']['changes'][0].keys()),
                         set(['id', 'date', 'status', 'rationaleTypes', 'rationale', 'rationale_ru', 'rationale_en', 'contractNumber']))

        self.app.authorization = None
        response = self.app.get('/contracts/{}/changes'.format(self.contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 1)
        self.assertEqual(set(response.json['data'][0].keys()),
                         set(['id', 'date', 'status', 'rationaleTypes', 'rationale', 'rationale_ru', 'rationale_en', 'contractNumber']))

    def test_create_change_invalid(self):
        response = self.app.post('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
        ])

        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      {'data': {}}, status=422)
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "rationaleTypes", "description": ["This field is required."]},
            {"location": "body", "name": "rationale", "description": ["This field is required."]}
        ])

        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      {'data': {'rationale': "", 'rationaleTypes': ['volumeCuts']}}, status=422)
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "rationale", "description": ["String value is too short."]}
        ])

        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      {'data': {'rationale_ua': ""}}, status=422)
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "rationale_ua", "description": "Rogue field"}
        ])
        self.app.authorization = None
        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      {'data': {'rationale_ua': "aaa"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/contracts/{}/changes'.format(self.contract['id']),
                                      {'data': {'rationale_ua': "aaa"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], self.contract_token),
                                       {'data': {'changes': [{'rationale': "penguin", 'rationaleTypes': ['volumeCuts']}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.body, 'null')

        response = self.app.get('/contracts/{}?acc_token={}'.format(self.contract['id'], self.contract_token))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('changes', response.json['data'])

    def test_create_change(self):
        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      {'data': {'rationale': u'причина зміни укр',
                                                'rationale_en': 'change cause en',
                                                'rationaleTypes': ['qualityImprovement']}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        change = response.json['data']
        self.assertEqual(change['status'], 'pending')
        self.assertIn('date', change)

        response = self.app.get('/contracts/{}/changes'.format(self.contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      {'data': {'rationale': u'трататата', 'rationaleTypes': ['priceReduction']}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "data", "description": "Can't create new contract change while any (pending) change exists"}
        ])

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'status': 'active'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      {'data': {'rationale': u'трататата', 'rationaleTypes': ['non-existing-rationale']}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "rationaleTypes", "description": [["Value must be one of ['volumeCuts', 'itemPriceVariation', 'qualityImprovement', 'thirdParty', 'durationExtension', 'priceReduction', 'taxRate', 'fiscalYearExtension']."]]}
        ])

        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      {'data': {'rationale': u'трататата', 'rationaleTypes': ['priceReduction']}})
        self.assertEqual(response.status, '201 Created')
        change2 = response.json['data']
        self.assertEqual(change2['status'], 'pending')

        response = self.app.get('/contracts/{}/changes'.format(self.contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 2)

    def test_patch_change(self):
        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      {'data': {'rationale': u'причина зміни укр',
                                                'rationale_en': u'change cause en',
                                                'rationaleTypes': ['priceReduction'],
                                                'contractNumber': u'№ 146'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        change = response.json['data']
        self.assertEqual(change['status'], 'pending')
        self.assertEqual(change['contractNumber'], u'№ 146')
        creation_date = change['date']

        now = get_now().isoformat()
        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'date': now}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.body, 'null')

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'rationale_ru': 'шота на руськом'}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('rationale_ru', response.json['data'])
        first_patch_date = response.json['data']['date']
        self.assertEqual(first_patch_date, creation_date)

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'rationale_en': 'another cause desctiption'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['rationale_en'], 'another cause desctiption')
        second_patch_date = response.json['data']['date']
        self.assertEqual(first_patch_date, second_patch_date)

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'rationaleTypes': ['fiscalYearExtension', 'priceReduction']}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['rationaleTypes'], ['fiscalYearExtension', 'priceReduction'])

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'rationaleTypes': ['fiscalYearExtension', 'volumeCuts', 'taxRate']}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['rationaleTypes'], ['fiscalYearExtension', 'volumeCuts', 'taxRate'])

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'rationaleTypes': 'fiscalYearExtension'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['rationaleTypes'], ['fiscalYearExtension'])

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'rationaleTypes': 'fiscalYearExtension, volumeCuts'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "rationaleTypes", "description": [["Value must be one of ['volumeCuts', 'itemPriceVariation', 'qualityImprovement', 'thirdParty', 'durationExtension', 'priceReduction', 'taxRate', 'fiscalYearExtension']."]]}
        ])

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                      {'data': {'rationaleTypes': []}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "rationaleTypes", "description": ["Please provide at least 1 item."]}
        ])

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'id': '1234' * 8}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.body, 'null')

        self.app.authorization = None
        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'rationale_en': 'la-la-la'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.patch_json('/contracts/{}/changes/{}'.format(self.contract['id'], change['id']),
                                       {'data': {'rationale_en': 'la-la-la'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'status': 'active'}})
        self.assertEqual(response.status, '200 OK')
        self.assertNotEqual(response.json['data']['date'], creation_date)
        self.assertNotEqual(response.json['data']['date'], first_patch_date)
        self.assertNotEqual(response.json['data']['date'], second_patch_date)

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                       {'data': {'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite())
    suite.addTest(unittest.makeSuite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
