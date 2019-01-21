# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.tests.base import test_organization

# TenderCancellationResourceTest


def create_tender_cancellation_invalid(self):
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


def create_tender_cancellation(self):
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reasonType'], 'cancelled')
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token),
        {'data': {'reason': 'first cancellation reason', 'reasonType': 'unsuccessful'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    first_cancellation = response.json['data']
    self.assertEqual(first_cancellation['reasonType'], 'unsuccessful')
    self.assertEqual(first_cancellation['reason'], 'first cancellation reason')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'second cancellation reason'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    second_cancellation = response.json['data']
    self.assertEqual(second_cancellation['reason'], 'second cancellation reason')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'third cancellation reason'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    third_cancellation = response.json['data']
    self.assertEqual(third_cancellation['reason'], 'third cancellation reason')

    response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
        self.tender_id, second_cancellation['id'], self.tender_token), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'cancelled')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add cancellation in current (cancelled) tender status")


def create_tender_cancellation_with_post(self):
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason', 'status': 'active'}})
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
    self.assertEqual(response.json['data']["status"], 'cancelled')


def create_cancellation_on_lot(self):
    """ Try create cancellation with cancellationOf = lot while tender hasn't lots """
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                  self.tender_token),
                                  {'data': {'reason': 'cancellation reason',
                                            'cancellationOf': 'lot',
                                            'relatedLot': "1" * 32}},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'],
                     [{
                         u"location": u"body",
                         u"name": u"relatedLot",
                         u"description": [u"relatedLot should be one of lots"]
                     },
                         {
                             u"location": u"body",
                             u"name": u"cancellationOf",
                             u"description": [
                                 u"Lot cancellation can not be submitted, since \"multiple lots\" option is not available for this type of tender."
                             ]
                         }])

# TenderNegotiationCancellationResourceTest


def negotiation_create_cancellation_on_lot(self):
        """ Try create cancellation with cancellationOf = lot while tender hasn't lots """
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': "1" * 32}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'],
                         [{u'description': [u'relatedLot should be one of lots'], u'location': u'body',
                          u'name': u'relatedLot'}])

# TenderNegotiationLotsCancellationResourceTest


def create_tender_lots_cancellation(self):
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
    self.assertEqual(response.json['data']["status"], 'active')

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

    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
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

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
    self.assertEqual(response.json['data']['lots'][1]["status"], 'cancelled')
    self.assertEqual(response.json['data']["status"], 'cancelled')


def cancelled_lot_without_relatedLot(self):
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            "cancellationOf": "lot"
        }},
        status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [{
        "location": "body",
        "name": "relatedLot",
        "description": ["This field is required."]
    }])


def delete_first_lot_second_cancel(self):
    """ One lot we delete another cancel and check tender status """
    self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                        {
                            "data": {
                                "items": [
                                    {
                                        "relatedLot": self.initial_lots[1]["id"]
                                    }
                                ]
                            }
                        })

    response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(
        self.tender_id, self.initial_lots[0]['id'], self.tender_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
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

    response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'cancelled')


def cancel_tender(self):
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "tender"
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertEqual(cancellation['status'], 'active')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])

    # Check tender
    response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))

    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'cancelled')

    # Check lots
    response = self.app.get('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][0]['status'], 'active')
    self.assertEqual(response.json['data'][1]['status'], 'active')


def create_cancellation_on_tender_with_one_complete_lot(self):
    lot = self.initial_lots[0]

    # Create award
    response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'suppliers': [test_organization], 'status': 'pending',
                                                      'qualified': True, 'value': {"amount": 469,
                                                                                   "currency": "UAH",
                                                                                   "valueAddedTaxIncluded": True},
                                                      'lotID': lot['id']}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'pending')

    # Activate award
    award = response.json['data']
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
        self.tender_id, award['id'], self.tender_token), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'active')

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        if i.get('complaintPeriod', {}):  # reporting procedure does not have complaintPeriod
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)

    # Sign contract
    response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
    response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
        self.tender_id, response.json['data'][0]['id'], self.tender_token), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'active')

    # Try to create cancellation on tender
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                  {'data': {'reason': 'cancellation reason',
                                            'status': 'active',
                                            "cancellationOf": "tender"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can\'t add cancellation, if there is at least one complete lot")


def cancellation_on_not_active_lot(self):
    lot = self.initial_lots[0]

    # Create cancellation on lot with status cancelled
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason',
                  'status': 'active',
                  "cancellationOf": "lot",
                  "relatedLot": lot['id']}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    # check lot status
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.json['data']['status'], 'cancelled')

    # Try to create cancellation on lot with status cancelled
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason',
                  'status': 'pending',
                  "cancellationOf": "lot",
                  "relatedLot": lot['id']}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add cancellation only in active lot status")
