# -*- coding: utf-8 -*-
import uuid
from copy import deepcopy
from openprocurement.agreement.core.tests.base import change_auth
from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.utils import get_now
from openprocurement.agreement.cfaua.tests.base import TEST_DOCUMENTS


# TestTenderAgreement


def create_agreement(self):
    data = self.initial_data
    data['id'] = uuid.uuid4().hex
    with change_auth(self.app, ('Basic', ('agreements', ''))) as app:
        response = self.app.post_json('/agreements', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['agreementID'], data['agreementID'])

    response = self.app.get('/agreements/{}'.format(data['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['id'], data['id'])


def create_agreement_with_documents(self):
    data = deepcopy(self.initial_data)
    data['id'] = uuid.uuid4().hex
    data['documents'] = TEST_DOCUMENTS
    with change_auth(self.app, ('Basic', ('agreements', ''))) as app:
        response = self.app.post_json('/agreements', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['agreementID'], data['agreementID'])

    response = self.app.get('/agreements/{}'.format(data['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['id'], data['id'])

    response = self.app.get('/agreements/{}/documents'.format(data['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), len(TEST_DOCUMENTS))


def create_agreement_with_features(self):
    data = deepcopy(self.initial_data)
    item = data['items'][0].copy()
    item['id'] = "1"
    data['items'] = [item]
    data['features'] = self.features
    parameters = {
        "parameters": [
            {
                "code": i["code"],
                "value": i['enum'][0]['value'],
            }
            for i in data['features']
        ]
    }

    for contract in data['contracts']:
        contract.update(parameters)

    response = self.app.post_json('/agreements', {'data': data})
    self.assertEqual((response.status, response.content_type), ('201 Created', 'application/json'))
    agreement = response.json['data']
    self.assertEqual(agreement['features'], data['features'])
    for contract in agreement['contracts']:
        self.assertEqual(contract['parameters'], parameters['parameters'])


def patch_agreement_features_invalid(self):
    data = deepcopy(self.initial_data)
    item = data['items'][0].copy()
    item['id'] = "1"
    data['items'] = [item]
    data['features'] = self.features

    response = self.app.post_json('/agreements', {'data': data})
    self.assertEqual((response.status, response.content_type), ('201 Created', 'application/json'))
    agreement = response.json['data']
    self.assertEqual(agreement['features'], data['features'])
    agreement = response.json['data']
    token = response.json['access']['token']

    self.app.authorization = ('Basic', ('broker', ''))
    new_features = deepcopy(data['features'])
    new_features[0]['code'] = 'OCDS-NEW-CODE'
    response = self.app.patch_json('/agreements/{}?acc_token={}'.format(
        agreement['id'], token), {'data': {'features': new_features}}, status=403)
    self.assertEqual((response.status, response.content_type), ('403 Forbidden', 'application/json'))
    self.assertEqual(response.json['errors'][0]['description'], "Can't change features")


# AgreementResources


def get_agreements_by_id(self):
    response = self.app.get('/agreements/{}'.format(self.agreement_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['id'], self.agreement_id)

    bad_agreement_id = uuid.uuid4().hex
    response = self.app.get('/agreements/{}'.format(bad_agreement_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')


def extract_credentials(self):
    tender_token = self.initial_data['tender_token']
    response = self.app.get('/agreements/{}'.format(self.agreement_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.patch_json(
        '/agreements/{}?acc_token={}'.format(
            self.agreement_id, tender_token
        ),
        {"data": {"status": "active"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')

    response = self.app.patch_json(
        '/agreements/{}/credentials?acc_token={}'.format(
            self.agreement_id, tender_token),
        {'data': ''}
    )
    self.assertEqual(response.status, '200 OK')
    token = response.json.get('access', {}).get('token')
    self.assertIsNotNone(token)
    doc = self.db.get(self.agreement_id)
    self.assertEqual(
        doc['owner_token'],
        token
    )


def agreement_patch_invalid(self):
    response = self.app.patch_json(
        '/agreements/{}/credentials?acc_token={}'.format(
            self.agreement_id, self.initial_data['tender_token']),
        {'data': ''}
    )
    self.assertEqual(response.status, '200 OK')

    token = response.json['access']['token']
    for data in [
        {"title": "new title"},
        {
            "items": [
              {
                "description": "description",
                "additionalClassifications": [
                  {
                    "scheme": u"ДКПП",
                    "id": "01.11.83-00.00",
                    "description": u"Арахіс лущений"
                  }
                ],
                "deliveryAddress": {
                  "postalCode": "11223",
                  "countryName": u"Україна",
                  "streetAddress": u"ываыпып",
                  "region": u"Київська обл.",
                  "locality": u"м. Київ"
                },
                "deliveryDate": {
                  "startDate": "2016-05-16T00:00:00+03:00",
                  "endDate": "2016-06-29T00:00:00+03:00"
                }
              }
            ],
        },
        {
            'procuringEntity': {
                "contactPoint": {
                    "email": "mail@gmail.com"
                },
                "identifier": {
                    "scheme": "UA-EDR",
                    "id": "111111111111111",
                    "legalName": u"Демо организатор (государственные торги)"
                },
                "name": u"Демо организатор (государственные торги)",
                "kind": "other",
                "address": {
                    "postalCode": "21027",
                    "countryName": "Україна",
                }
            }
        }
    ]:
        response = self.app.patch_json(
            '/agreements/{}?acc_token={}'.format(self.agreement_id, token), {'data': data})
        self.assertEqual(response.status, '200 OK')
        self.assertIsNone(response.json)

    response = self.app.patch_json('/agreements/{}?acc_token={}'.format(
        self.agreement_id, token), {'data': {'status': 'terminated'}})

    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'terminated')
    response = self.app.patch_json(
        '/agreements/{}/credentials?acc_token={}'.format(self.agreement_id, self.initial_data['tender_token']),
        {'data': ''}, status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'], [
                     {u'description': u"Can't generate credentials in current (terminated)"
                                      u" agreement status", u'location': u'body', u'name': u'data'}]
                     )


# AgreementListingTests


def empty_listing(self):
    response = self.app.get('/agreements')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertNotIn('{\n    "', response.body)
    self.assertNotIn('callback({', response.body)
    self.assertEqual(response.json['next_page']['offset'], '')
    self.assertNotIn('prev_page', response.json)

    response = self.app.get('/agreements?opt_jsonp=callback')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertNotIn('{\n    "', response.body)
    self.assertIn('callback({', response.body)

    response = self.app.get('/agreements?opt_pretty=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)
    self.assertNotIn('callback({', response.body)

    response = self.app.get('/agreements?opt_jsonp=callback&opt_pretty=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('{\n    "', response.body)
    self.assertIn('callback({', response.body)

    response = self.app.get('/agreements?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertIn('descending=1', response.json['next_page']['uri'])
    self.assertIn('limit=10', response.json['next_page']['uri'])
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertIn('limit=10', response.json['prev_page']['uri'])

    response = self.app.get('/agreements?feed=changes')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertEqual(response.json['next_page']['offset'], '')
    self.assertNotIn('prev_page', response.json)

    response = self.app.get('/agreements?feed=changes&offset=0', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Offset expired/invalid', u'location': u'params', u'name': u'offset'}
    ])

    response = self.app.get('/agreements?feed=changes&descending=1&limit=10')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertIn('descending=1', response.json['next_page']['uri'])
    self.assertIn('limit=10', response.json['next_page']['uri'])
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertIn('limit=10', response.json['prev_page']['uri'])


def listing(self):
    response = self.app.get('/agreements')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    agreements = []

    for i in range(3):
        data = deepcopy(self.initial_data)
        data['id'] = uuid.uuid4().hex
        offset = get_now().isoformat()
        with change_auth(self.app, ('Basic', ('agreements', ''))) as app:
            response = self.app.post_json('/agreements', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        agreements.append(response.json['data'])

    ids = ','.join([i['id'] for i in agreements])

    while True:
        response = self.app.get('/agreements')
        self.assertEqual(response.status, '200 OK')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(','.join([i['id'] for i in response.json['data']]), ids)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in agreements]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]),
                     set([i['dateModified'] for i in agreements]))
    self.assertEqual([i['dateModified'] for i in response.json['data']],
                     sorted([i['dateModified'] for i in agreements]))

    response = self.app.get('/agreements?offset={}'.format(offset))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/agreements?limit=2')
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

    response = self.app.get('/agreements', params=[('opt_fields', 'agreementID')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'agreementID']))
    self.assertIn('opt_fields=agreementID', response.json['next_page']['uri'])

    response = self.app.get('/agreements?descending=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in agreements]))
    self.assertEqual([i['dateModified'] for i in response.json['data']],
                     sorted([i['dateModified'] for i in agreements], reverse=True))

    response = self.app.get('/agreements?descending=1&limit=2')
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

    test_agreement_data2 = deepcopy(self.initial_data)
    test_agreement_data2['mode'] = 'test'
    response = self.app.post_json('/agreements', {'data': test_agreement_data2})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    while True:
        response = self.app.get('/agreements?mode=test')
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/agreements?mode=_all_')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 4)

    response = self.app.get('/agreements?mode=_all_&opt_fields=status')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 4)
