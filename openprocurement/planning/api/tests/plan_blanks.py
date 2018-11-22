# -*- coding: utf-8 -*-
import mock
from copy import deepcopy

from datetime import datetime, timedelta

from iso8601 import parse_date
from openprocurement.api.constants import ROUTE_PREFIX, CPV_ITEMS_CLASS_FROM, \
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM, TZ
from openprocurement.api.utils import get_now

from openprocurement.planning.api.models import Plan
from openprocurement.planning.api.constants import PROCEDURES


# PlanTest


def simple_add_plan(self):
    u = Plan(self.initial_data)
    u.planID = "UA-P-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.planID == fromdb['planID']
    assert u.doc_type == "Plan"

    u.delete_instance(self.db)


# AccreditationPlanTest


def create_plan_accreditation(self):
    self.app.authorization = ('Basic', ('broker3', ''))
    response = self.app.post_json('/plans', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    for broker in ['broker2', 'broker4']:
        self.app.authorization = ('Basic', (broker, ''))
        response = self.app.post_json('/plans', {"data": self.initial_data}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Broker Accreditation level does not permit plan creation")

    self.app.authorization = ('Basic', ('broker1t', ''))
    response = self.app.post_json('/plans', {"data": self.initial_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Broker Accreditation level does not permit plan creation")

    response = self.app.post_json('/plans', {"data": self.initial_data_mode_test})
    self.assertEqual(response.status, '201 Created')


# PlanResourceTest


def empty_listing(self):
    response = self.app.get('/plans')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertNotIn('{\n    "', response.body)
    self.assertNotIn('callback({', response.body)
    self.assertEqual(response.json['next_page']['offset'], '')
    self.assertNotIn('prev_page', response.json)

    response = self.app.get('/plans?opt_jsonp=callback')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertNotIn('{\n    "', response.body)
    self.assertIn('callback({', response.body)

    response = self.app.get('/plans?opt_pretty=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)
    self.assertNotIn('callback({', response.body)

    response = self.app.get('/plans?opt_jsonp=callback&opt_pretty=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('{\n    "', response.body)
    self.assertIn('callback({', response.body)

    response = self.app.get('/plans?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertIn('descending=1', response.json['next_page']['uri'])
    self.assertIn('limit=10', response.json['next_page']['uri'])
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertIn('limit=10', response.json['prev_page']['uri'])

    response = self.app.get('/plans?feed=changes')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertEqual(response.json['next_page']['offset'], '')
    self.assertNotIn('prev_page', response.json)

    response = self.app.get('/plans?feed=changes&offset=0', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Offset expired/invalid', u'location': u'params', u'name': u'offset'}
    ])

    response = self.app.get('/plans?feed=changes&descending=1&limit=10')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertIn('descending=1', response.json['next_page']['uri'])
    self.assertIn('limit=10', response.json['next_page']['uri'])
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertIn('limit=10', response.json['prev_page']['uri'])


def listing(self):
    response = self.app.get('/plans')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    plans = []

    for i in range(3):
        offset = get_now().isoformat()
        response = self.app.post_json('/plans', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        plans.append(response.json['data'])

    ids = ','.join([i['id'] for i in plans])

    while True:
        response = self.app.get('/plans')
        self.assertEqual(response.status, '200 OK')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(','.join([i['id'] for i in response.json['data']]), ids)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in plans]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]),
                     set([i['dateModified'] for i in plans]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in plans]))

    response = self.app.get('/plans?offset={}'.format(offset))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/plans?limit=2')
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

    response = self.app.get('/plans', params=[('opt_fields', 'budget')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertNotIn('opt_fields=budget', response.json['next_page']['uri'])

    response = self.app.get('/plans', params=[('opt_fields', 'planID')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'planID']))
    self.assertIn('opt_fields=planID', response.json['next_page']['uri'])

    response = self.app.get('/plans?descending=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in plans]))
    self.assertEqual([i['dateModified'] for i in response.json['data']],
                     sorted([i['dateModified'] for i in plans], reverse=True))

    response = self.app.get('/plans?descending=1&limit=2')
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

    test_plan_data2 = self.initial_data.copy()
    test_plan_data2['mode'] = 'test'
    response = self.app.post_json('/plans', {'data': test_plan_data2})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    while True:
        response = self.app.get('/plans?mode=test')
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/plans?mode=_all_')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 4)


def listing_changes(self):
    response = self.app.get('/plans?feed=changes')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    plans = []

    for i in range(3):
        response = self.app.post_json('/plans', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        plans.append(response.json['data'])

    ids = ','.join([i['id'] for i in plans])

    while True:
        response = self.app.get('/plans?feed=changes')
        self.assertEqual(response.status, '200 OK')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(','.join([i['id'] for i in response.json['data']]), ids)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in plans]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]),
                     set([i['dateModified'] for i in plans]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in plans]))

    response = self.app.get('/plans?feed=changes&limit=2')
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

    response = self.app.get('/plans?feed=changes', params=[('opt_fields', 'budget')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertNotIn('opt_fields=budget', response.json['next_page']['uri'])

    response = self.app.get('/plans?feed=changes', params=[('opt_fields', 'planID')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'planID']))
    self.assertIn('opt_fields=planID', response.json['next_page']['uri'])

    response = self.app.get('/plans?feed=changes&descending=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in plans]))
    self.assertEqual([i['dateModified'] for i in response.json['data']],
                     sorted([i['dateModified'] for i in plans], reverse=True))

    response = self.app.get('/plans?feed=changes&descending=1&limit=2')
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

    test_plan_data2 = self.initial_data.copy()
    test_plan_data2['mode'] = 'test'
    response = self.app.post_json('/plans', {'data': test_plan_data2})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    while True:
        response = self.app.get('/plans?mode=test')
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/plans?feed=changes&mode=_all_')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 4)


def create_plan_invalid(self):
    request_path = '/plans'
    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description':
             u"Content-Type header should be one of ['application/json']", u'location': u'header',
         u'name': u'Content-Type'}
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

    response = self.app.post_json(request_path, {'data': {
        'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(request_path, {'data': {'budget': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [
            u'Please use a mapping for this field or Budget instance instead of unicode.'], u'location': u'body',
            u'name': u'budget'}
    ])

    response = self.app.post_json(request_path, {'data': {'tender': {'procurementMethod': 'invalid_value'}}},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'procuringEntity'},
                  response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'classification'},
                  response.json['errors'])

    data = self.initial_data['tender']
    self.initial_data['tender'] = {'procurementMethod': 'open', 'procurementMethodType': 'reporting',
                                   'tenderPeriod': data['tenderPeriod']}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['tender'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertIn(
        {u'description': {u'procurementMethodType': [
            u"Value must be one of {!r}.".format(PROCEDURES['open'])
        ]}, u'location': u'body', u'name': u'tender'},
        response.json['errors'])

    data = self.initial_data['tender']
    self.initial_data['tender'] = {'procurementMethod': 'limited', 'procurementMethodType': 'belowThreshold',
                                   'tenderPeriod': data['tenderPeriod']}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['tender'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertIn(
        {u'description': {u'procurementMethodType': [
            u"Value must be one of {!r}.".format(PROCEDURES['limited'])
        ]}, u'location': u'body', u'name': u'tender'},
        response.json['errors'])

    response = self.app.post_json(request_path,
                                  {'data': {'tender': {'tenderPeriod': {'startDate': 'invalid_value'}}}},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'tenderPeriod': {u'startDate': [u'Could not parse invalid_value. Should be ISO8601.']}},
         u'location': u'body', u'name': u'tender'}
    ])

    response = self.app.post_json(request_path, {
        'data': {'tender': {'tenderPeriod': {'startDate': '9999-12-31T23:59:59.999999'}}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'tenderPeriod': {u'startDate': [u'date value out of range']}}, u'location': u'body',
         u'name': u'tender'}
    ])

    additionalClassifications = [i.pop("additionalClassifications") for i in self.initial_data["items"]]
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = self.initial_data['classification']['id']
        cpv_codes = [i['classification']['id'] for i in self.initial_data["items"]]
        self.initial_data['classification']['id'] = '99999999-9'
        for index, cpv_code in enumerate(cpv_codes):
            self.initial_data["items"][index]['classification']['id'] = '99999999-9'

    if get_now() < NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM:
        response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'additionalClassifications': [u'This field is required.']},
                              {u'additionalClassifications': [u'This field is required.']},
                              {u'additionalClassifications': [u'This field is required.']}], u'location': u'body',
             u'name': u'items'}
        ])

    for index, additionalClassification in enumerate(additionalClassifications):
        self.initial_data["items"][index]['additionalClassifications'] = additionalClassification
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.initial_data['classification']['id'] = cpv_code
        for index, cpv_code in enumerate(cpv_codes):
            self.initial_data["items"][index]['classification']['id'] = cpv_code

    additionalClassifications = [i["additionalClassifications"][0]["scheme"] for i in self.initial_data["items"]]
    for index, _ in enumerate(additionalClassifications):
        self.initial_data["items"][index]["additionalClassifications"][0]["scheme"] = u'Не ДКПП'
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = self.initial_data['classification']['id']
        cpv_codes = [i['classification']['id'] for i in self.initial_data["items"]]
        self.initial_data['classification']['id'] = '99999999-9'
        for index, cpv_code in enumerate(cpv_codes):
            self.initial_data["items"][index]['classification']['id'] = '99999999-9'
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    for index, data in enumerate(additionalClassifications):
        self.initial_data["items"][index]["additionalClassifications"][0]["scheme"] = data
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.initial_data['classification']['id'] = cpv_code
        for index, cpv_code in enumerate(cpv_codes):
            self.initial_data["items"][index]['classification']['id'] = cpv_code
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'additionalClassifications': [
                u"One of additional classifications should be one of [ДК003, ДК015, ДК018, specialNorms]."]} for _ in
                              additionalClassifications], u'location': u'body', u'name': u'items'}
        ])
    else:
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'additionalClassifications': [
                u"One of additional classifications should be one of [ДКПП, NONE, ДК003, ДК015, ДК018]."]} for _ in
                              additionalClassifications], u'location': u'body', u'name': u'items'}
        ])

    data = self.initial_data["procuringEntity"]["name"]
    del self.initial_data["procuringEntity"]["name"]
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["procuringEntity"]["name"] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'name': [u'This field is required.']}, u'location': u'body', u'name': u'procuringEntity'}
    ])

    data = self.initial_data["budget"]
    del self.initial_data["budget"]
    self.initial_data['tender']['procurementMethodType'] = 'belowThreshold'
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["budget"] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'budget'}
    ])

    data = self.initial_data["items"][0].copy()
    classification = data['classification'].copy()
    classification["id"] = u'31519200-9'
    data['classification'] = classification
    self.initial_data["items"] = [self.initial_data["items"][0], data]
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'classification': [u'CPV class of items should be identical to root cpv']}],
             u'location': u'body', u'name': u'items'}
        ])
    else:
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'classification': [u'CPV group of items be identical to root cpv']}],
             u'location': u'body', u'name': u'items'}
        ])

    classification_id = self.initial_data["classification"]["id"]
    self.initial_data["classification"]["id"] = u'33600000-6'
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["classification"]["id"] = classification_id
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'classification': [u'CPV group of items be identical to root cpv']}],
         u'location': u'body', u'name': u'items'}
    ])

    classification_id = self.initial_data["classification"]["id"]
    self.initial_data["classification"]["id"] = u'33600000-6'
    item = self.initial_data["items"][0].copy()
    data = self.initial_data["items"][0].copy()
    classification = data['classification'].copy()
    classification["id"] = u'33610000-9'
    data['classification'] = classification
    data2 = self.initial_data["items"][0].copy()
    classification = data2['classification'].copy()
    classification["id"] = u'33620000-2'
    data2['classification'] = classification
    self.initial_data["items"] = [data, data2]
    response = self.app.post_json(request_path, {'data': self.initial_data})
    self.initial_data["classification"]["id"] = classification_id
    self.initial_data["items"] = [item]
    self.assertEqual(response.status, '201 Created')


def create_plan_generated(self):
    data = self.initial_data.copy()
    data.update({'id': 'hash', 'doc_id': 'hash2', 'planID': 'hash3'})
    response = self.app.post_json('/plans', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    plan = response.json['data']
    self.assertEqual(set(plan), set([
        u'id', u'dateModified', u'datePublished', u'planID', u'budget', u'tender',
        u'classification', u'additionalClassifications', u'items', u'procuringEntity', u'owner'
    ]))
    self.assertNotEqual(data['id'], plan['id'])
    self.assertNotEqual(data['doc_id'], plan['id'])
    self.assertNotEqual(data['planID'], plan['planID'])


def create_plan(self):
    response = self.app.get('/plans')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/plans', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    plan = response.json['data']
    self.assertEqual(set(plan) - set(self.initial_data),
                     set([u'id', u'dateModified', u'datePublished', u'planID', u'owner']))
    self.assertIn(plan['id'], response.headers['Location'])

    response = self.app.get('/plans/{}'.format(plan['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(plan))
    self.assertEqual(response.json['data'], plan)

    response = self.app.post_json('/plans?opt_jsonp=callback', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('callback({"', response.body)

    response = self.app.post_json('/plans?opt_pretty=1', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)

    response = self.app.post_json('/plans', {"data": self.initial_data, "options": {"pretty": True}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)

    response = self.app.post_json('/plans', {"data": self.initial_data_with_year}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [{
        u"description": {u"year": [
            u"Can't use year field, use period field instead"
        ]}, u"location": u"body", u"name": u"budget",
    }])


def get_plan(self):
    response = self.app.get('/plans')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/plans', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    plan = response.json['data']

    response = self.app.get('/plans/{}'.format(plan['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], plan)

    response = self.app.get('/plans/{}?opt_jsonp=callback'.format(plan['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('callback({"data": {"', response.body)

    response = self.app.get('/plans/{}?opt_pretty=1'.format(plan['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "data": {\n        "', response.body)


def patch_plan(self):
    response = self.app.get('/plans')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/plans', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    plan = response.json['data']
    dateModified = plan.pop('dateModified')

    response = self.app.patch_json('/plans/{}'.format(plan['id']),
                                   {'data': {'budget': {'id': u"12303111000-3"}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    new_plan = response.json['data']
    new_dateModified = new_plan.pop('dateModified')
    plan['budget']['id'] = u"12303111000-3"
    self.assertEqual(plan, new_plan)
    self.assertNotEqual(dateModified, new_dateModified)

    response = self.app.patch_json('/plans/{}'.format(
        plan['id']), {'data': {'dateModified': new_dateModified}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    new_plan2 = response.json['data']
    new_dateModified2 = new_plan2.pop('dateModified')
    self.assertEqual(new_plan, new_plan2)
    self.assertEqual(new_dateModified, new_dateModified2)

    revisions = self.db.get(plan['id']).get('revisions')
    self.assertEqual(revisions[-1][u'changes'][0]['op'], u'replace')
    self.assertEqual(revisions[-1][u'changes'][0]['path'], u'/budget/id')

    response = self.app.get('/plans/{}/revisions'.format(plan['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['revisions'], revisions)

    response = self.app.patch_json('/plans/{}'.format(
        plan['id']), {'data': {'items': [self.initial_data['items'][0]]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/plans/{}'.format(
        plan['id']), {'data': {'items': [{}, self.initial_data['items'][0]]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    item0 = response.json['data']['items'][0]
    item1 = response.json['data']['items'][1]
    self.assertNotEqual(item0.pop('id'), item1.pop('id'))
    self.assertEqual(item0, item1)

    response = self.app.patch_json('/plans/{}'.format(
        plan['id']), {'data': {'items': [{}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']['items']), 1)

    response = self.app.patch_json('/plans/{}'.format(plan['id']), {'data': {'items': [{"classification": {
        "scheme": "ДК021",
        "id": "03117140-7",
        "description": "Послуги з харчування у школах"
    }}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/plans/{}'.format(plan['id']),
                                   {'data': {'items': [{"additionalClassifications": [
                                       plan['items'][0]["additionalClassifications"][0] for i in range(3)
                                   ]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/plans/{}'.format(plan['id']), {
        'data': {'items': [{"additionalClassifications": plan['items'][0]["additionalClassifications"]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/plans/{}'.format(
        plan['id']), {'data': {'tender': {'tenderPeriod': {'startDate': new_dateModified2}}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    new_plan = response.json['data']
    self.assertIn('startDate', new_plan['tender']['tenderPeriod'])

    response = self.app.patch_json('/plans/{}'.format(
        plan['id']), {'data': {'budget': {'period': {'endDate': datetime(
            year=datetime.now().year + 2, month=12, day=31
        ).isoformat()}}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'period': {u'endDate': [
            u'Period startDate and endDate must be within one year for belowThreshold.'
        ]}}, u'location': u'body', u'name': u'budget'}
    ])

    # delete items
    response = self.app.patch_json('/plans/{}'.format(plan['id']), {'data': {'items': []}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('items', response.json['data'])


def plan_not_found(self):
    response = self.app.get('/plans')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.get('/plans/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'plan_id'}
    ])

    response = self.app.patch_json(
        '/plans/some_id', {'data': {}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'plan_id'}
    ])


def esco_plan(self):
    response = self.app.get('/plans')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    data = deepcopy(self.initial_data)
    budget = data.pop('budget')
    data['tender']['procurementMethodType'] = 'esco'
    response = self.app.post_json('/plans', {"data": data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    plan = response.json['data']
    self.assertEqual(
        set(plan) - set(self.initial_data),
        set([u'id', u'dateModified', u'datePublished', u'planID', u'owner']))
    self.assertNotIn('budget', plan)
    self.assertIn(plan['id'], response.headers['Location'])

    data['budget'] = budget
    response = self.app.post_json('/plans', {"data": data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    plan = response.json['data']
    self.assertEqual(
        set(plan) - set(self.initial_data),
        set([u'id', u'dateModified', u'datePublished', u'planID', u'owner']))
    self.assertIn('budget', plan)
    self.assertIn(plan['id'], response.headers['Location'])


def cfaua_plan(self):
    response = self.app.get('/plans')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    data = deepcopy(self.initial_data)
    data['tender']['procurementMethodType'] = 'closeFrameworkAgreementUA'
    data['budget']['period']['endDate'] = datetime(
        year=datetime.now().year + 2, month=12, day=31
    ).isoformat()
    response = self.app.post_json('/plans', {"data": data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    plan = response.json['data']
    self.assertEqual(
        set(plan) - set(self.initial_data),
        set([u'id', u'dateModified', u'datePublished', u'planID', u'owner']))
    self.assertIn('budget', plan)
    period = plan['budget']['period']
    self.assertNotEqual(
        parse_date(period['startDate']).year,
        parse_date(period['endDate']).year)
    self.assertIn(plan['id'], response.headers['Location'])

    response = self.app.patch_json('/plans/{}'.format(
        plan['id']), {'data': {'budget': {'period': {'endDate': datetime(
            year=datetime.now().year + 5, month=12, day=31
        ).isoformat()}}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'period': {u'endDate': [
            u'Period startDate and endDate must be within 5 budget years for closeFrameworkAgreementUA.'
        ]}}, u'location': u'body', u'name': u'budget'}
    ])


def create_plan_budget_year(self):
    response = self.app.get('/plans')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/plans', {"data": self.initial_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [{
        u"description": {u"period": [
            u"Can't use period field, use year field instead"
        ]}, u"location": u"body", u"name": u"budget",
    }])

    response = self.app.post_json('/plans', {"data": self.initial_data_with_year})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    plan = response.json['data']
    self.assertEqual(
        set(plan) - set(self.initial_data_with_year),
        set([u'id', u'dateModified', u'datePublished', u'planID', u'owner']))
    self.assertIn(plan['id'], response.headers['Location'])
    self.assertIn('year', plan['budget'])

def patch_plan_budget_year(self):
    response = self.app.post_json('/plans', {"data": self.initial_data_with_year})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    plan = response.json['data']
    self.assertIn('year', plan['budget'])

    with mock.patch('openprocurement.planning.api.models.BUDGET_PERIOD_FROM', get_now() - timedelta(days=1)):
        response = self.app.patch_json(
            '/plans/{}'.format(plan['id']),
            {"data": self.initial_data})
        plan = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('year', plan['budget'])
