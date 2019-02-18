# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from isodate import duration_isoformat
from uuid import uuid4

from openprocurement.tender.cfaua.constants import CLARIFICATIONS_UNTIL_PERIOD, MAX_AGREEMENT_PERIOD
from openprocurement.tender.cfaua.tests.base import agreement_period
from openprocurement.tender.cfaua.models.submodels.agreement import Agreement


# TenderAgreementResourceTest

def get_tender_agreement(self):
    agreement_raw = self.app.app.registry.db.get(self.tender_id)['agreements'][0]
    agreement = Agreement(agreement_raw).serialize("embedded")

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/agreements/{}'.format(self.tender_id, agreement['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], agreement)
    self.assertEqual(response.json['data']['status'], 'pending')

    response = self.app.get('/tenders/{}/agreements/some_id'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'agreement_id'}])

    response = self.app.get('/tenders/some_id/agreements/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}])


def get_tender_agreements(self):
    agreement_keys = tuple(['id', 'agreementID', 'items', 'status', 'contracts', 'date'])
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    for key in agreement_keys:
        self.assertIn(key, response.json['data'][0].keys())

    response = self.app.get('/tenders/some_id/agreements', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}])


def patch_tender_agreement_datesigned(self):
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    agreement = response.json['data'][0]
    self.assertEqual(agreement['status'], 'pending')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']
    self.assertEqual(tender['status'], 'active.awarded')

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active", "period": agreement_period}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'],
        [{
            u"description": u"Can't sign agreement without all contracts.unitPrices.value.amount",
            u'location': u'body',
            u'name': u'data'
        }]
    )

    # Fill unitPrice.value.amount for all contracts in agreement
    response = self.app.get('/tenders/{}/agreements/{}/contracts'.format(self.tender_id, self.agreement_id))
    contracts = response.json['data']
    for contract in contracts:
        unit_prices = contract['unitPrices']
        for unit_price in unit_prices:
            unit_price['value']['amount'] = 60
        response = self.app.patch_json(
            '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                         contract['id'], self.tender_token),
            {'data': {'unitPrices': unit_prices}}
        )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "dateSigned": tender['awardPeriod']['endDate']}, "period": agreement_period},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(
        response.json['errors'],
        [{
            "location": "body",
            "name": "dateSigned",
            "description": [
                "Agreement signature date should be after award complaint period end date ({})".format(
                    tender['awardPeriod']['endDate']
                )
            ]
        }]
    )

    # Set first contract.status in unsuccessful
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     contracts[0]['id'], self.tender_token),
        {'data': {'status': 'unsuccessful'}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'unsuccessful')

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": agreement_period}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'],
                     [{u'description': u"Agreement don't reach minimum active contracts.",
                       u'location': u'body',
                       u'name': u'data'}])

    # Set first contract.status in active
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     contracts[0]['id'], self.tender_token),
        {'data': {'status': 'active'}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'active')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']

    # Agreement signing
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": agreement_period}},
        status=403
    )
    end_date = tender['contractPeriod']['clarificationsUntil']
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'],
        [{
            "location": "body",
            "name": "data",
            "description":
                "Agreement signature date should be after contractPeriod.clarificationsUntil ({})".format(end_date)
        }]
    )

    tender = self.db.get(self.tender_id)
    tender['contractPeriod']['startDate'] = (datetime.now() - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1)).isoformat()
    tender['contractPeriod']['clarificationsUntil'] = (datetime.now()- timedelta(days=1)).isoformat()
    self.db.save(tender)

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": {'startDate': datetime.now().isoformat()}}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'startDate and endDate are required in agreement.period.',
                       u'location': u'body',
                       u'name': u'data'}])

    now = datetime.now()
    start_date = now.isoformat()
    end_date = (now + timedelta(days=465 * 5)).isoformat()

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": {'startDate': start_date, 'endDate': end_date}}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'],
        [{u'description':
            u"Agreement period can't be greater than {}.".format(duration_isoformat(MAX_AGREEMENT_PERIOD)),
          u'location': u'body',
          u'name': u'data'}])

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": agreement_period}}
    )
    contract = response.json['data']['contracts'][0]

    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertIn(u"dateSigned", response.json['data'].keys())

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "cancelled"}}, status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'],
                     [{u'description': u"Can't update agreement in current (complete) tender status",
                       u'location': u'body', u'name': u'data'}])

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'complete')

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, agreement['id'], contract['id'],
                                                                     self.tender_token),
        {'data': {'unitPrices': contract['unitPrices']}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'],
                     [{"location": "body",
                       "name": "data",
                       "description": "Can't update agreement in current (complete) tender status"}])


def agreement_termination(self):
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    agreement = response.json['data'][0]

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "terminated"}},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'][0]["description"],
                     [u"Value must be one of ['pending', 'active', 'cancelled', 'unsuccessful']."])


def agreement_cancellation(self):
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']
    self.assertEqual(tender['status'], 'active.awarded')

    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    agreement = response.json['data'][0]

    # Try sign agreement
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'],
        [{u'description': u'Period is required for agreement signing.', u'location': u'body', u'name': u'data'}]
    )

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active", "period": agreement_period}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'],
                     [{u'description': u"Can't sign agreement without all contracts.unitPrices.value.amount",
                       u'location': u'body',
                       u'name': u'data'}])

    # Agreement cancellation
    response = self.app.get('/tenders/{}/agreements/{}'.format(self.tender_id, agreement['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "pending")
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "cancelled"}}, status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'],
                     [{u'description': u"Can't update agreement status", u'location': u'body', u'name': u'data'}])


def create_tender_agreement_document(self):
    response = self.app.post(
        '/tenders/{}/agreements/{}/documents?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                  self.tender_token),
        upload_files=[('file', 'name.doc', 'content')]
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/agreements/{}/documents'.format(self.tender_id, self.agreement_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/tenders/{}/agreements/{}/documents?all=true'.format(self.tender_id, self.agreement_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get(
        '/tenders/{}/agreements/{}/documents/{}?download=some_id'.format(self.tender_id, self.agreement_id, doc_id),
        status=404
    )
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'download'}])

    response = self.app.get(
        '/tenders/{}/agreements/{}/documents/{}?{}'.format(self.tender_id, self.agreement_id, doc_id, key)
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, 'content')

    response = self.app.get('/tenders/{}/agreements/{}/documents/{}'.format(self.tender_id, self.agreement_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    self.cancel_tender()

    response = self.app.post(
        '/tenders/{}/agreements/{}/documents?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                  self.tender_token),
        upload_files=[('file', 'name.doc', 'content')],
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (cancelled) tender status")


def put_tender_agreement_document(self):
    response = self.app.post(
        '/tenders/{}/agreements/{}/documents?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        upload_files=[('file', 'name.doc', 'content')]
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put(
        '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(self.tender_id, self.agreement_id, doc_id,
                                                                     self.tender_token),
        status=404,
        upload_files=[('invalid_name', 'name.doc', 'content')]
    )
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'body', u'name': u'file'}])

    response = self.app.put(
        '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(self.tender_id, self.agreement_id, doc_id,
                                                                     self.tender_token),
        upload_files=[('file', 'name.doc', 'content2')]
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get(
        '/tenders/{}/agreements/{}/documents/{}?{}'.format(self.tender_id, self.agreement_id, doc_id, key)
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content2')

    response = self.app.get('/tenders/{}/agreements/{}/documents/{}'.format(self.tender_id, self.agreement_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put(
        '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(self.tender_id, self.agreement_id, doc_id,
                                                                     self.tender_token),
        'content3',
        content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get(
        '/tenders/{}/agreements/{}/documents/{}?{}'.format(self.tender_id, self.agreement_id, doc_id, key)
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content3')

    self.cancel_tender()

    response = self.app.put(
        '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(self.tender_id, self.agreement_id, doc_id,
                                                                     self.tender_token),
        upload_files=[('file', 'name.doc', 'content3')],
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (cancelled) tender status")



def patch_tender_agreement_document(self):
    response = self.app.post(
        '/tenders/{}/agreements/{}/documents?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        upload_files=[('file', 'name.doc', 'content')]
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(self.tender_id, self.agreement_id, doc_id,
                                                                     self.tender_token),
        {"data": {"description": "document description"}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get('/tenders/{}/agreements/{}/documents/{}'.format(self.tender_id, self.agreement_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])

    self.cancel_tender()

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(self.tender_id, self.agreement_id, doc_id,
                                                                     self.tender_token),
        {"data": {"description": "document description"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (cancelled) tender status")


def patch_tender_agreement(self):
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    agreement = response.json['data'][0]

    fake_agreementID = "myselfID"
    fake_items_data = [{"description": "New Description"}]

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"agreementID": fake_agreementID, "items": fake_items_data}}
    )
    response = self.app.get('/tenders/{}/agreements/{}'.format(self.tender_id, agreement['id']))
    self.assertNotEqual(fake_agreementID, response.json['data']['agreementID'])
    self.assertNotEqual(fake_items_data, response.json['data']['items'])

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active", "period": agreement_period}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'],
                     [{u'description': u"Can't sign agreement without all contracts.unitPrices.value.amount",
                       u'location': u'body',
                       u'name': u'data'}])

    # Fill unitPrice.value.amount for all contracts in agreement
    response = self.app.get('/tenders/{}/agreements/{}/contracts'.format(self.tender_id, self.agreement_id))
    contracts = response.json['data']
    for contract in contracts:
        unit_prices = contract['unitPrices']
        for unit_price in unit_prices:
            unit_price['value']['amount'] = 60
        response = self.app.patch_json(
            '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                         contract['id'], self.tender_token),
            {'data': {'unitPrices': unit_prices}}
        )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']

    # Sign agreement
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": agreement_period}},
        status=403
    )
    end_date = tender['contractPeriod']['clarificationsUntil']
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'],
        [{
            "location": "body",
            "name": "data",
            "description":
                "Agreement signature date should be after contractPeriod.clarificationsUntil ({})".format(end_date)
        }]
    )


    tender = self.db.get(self.tender_id)
    tender['contractPeriod']['startDate'] = (datetime.now() - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1)).isoformat()
    tender['contractPeriod']['clarificationsUntil'] = (datetime.now()- timedelta(days=1)).isoformat()
    self.db.save(tender)

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": agreement_period}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'active')
    self.assertIn(u"dateSigned", response.json['data'].keys())
    response = self.get_tender('')
    # Tender complete
    self.assertEqual(response.json['data']["status"], "complete")

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {
            "data": {
                "agreementID": "myselfID",
                "title": "New Title",
                "items": [{"description": "New Description"}],
            }
        },
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update agreement in current (complete) tender status")

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update agreement in current (complete) tender status")

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "pending"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update agreement in current (complete) tender status")

    response = self.app.patch_json('/tenders/{}/agreements/some_id'.format(self.tender_id),
                                   {"data": {"status": "active"}},
                                   status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'agreement_id'}])

    response = self.app.patch_json('/tenders/some_id/agreements/some_id', {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}])

    response = self.app.get('/tenders/{}/agreements/{}'.format(self.tender_id, agreement['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(
        self.tender_id, self.agreement_id, self.tender_token), {"data": {"status": "cancelled"}}, status=403)
    self.assertEqual((response.status, response.content_type), ('403 Forbidden', 'application/json'))
    self.assertEqual(response.json['errors'],
                     [{u'description': u"Can't update agreement in current (complete) tender status",
                       u'location': u'body', u'name': u'data'}])


def patch_tender_agreement_unsuccessful(self):

    self.set_status('active.awarded')
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['status'], 'active.awarded')

    response = self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(
        self.tender_id, self.agreement_id, self.tender_token), {"data": {"status": "unsuccessful"}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['status'], 'unsuccessful')

    response = self.app.get('/tenders/{}/agreements/{}'.format(self.tender_id, self.agreement_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")

    response = self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(
        self.tender_id, self.agreement_id, self.tender_token), {"data": {"status": "cancelled"}}, status=403)
    self.assertEqual((response.status, response.content_type), ('403 Forbidden', 'application/json'))
    self.assertEqual(response.json['errors'],
                     [{u'description': u"Can't update agreement in current (unsuccessful) tender status",
                       u'location': u'body', u'name': u'data'}])

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def not_found(self):
    response = self.app.post('/tenders/some_id/agreements/some_id/documents?acc_token={}'.format(self.tender_token),
                             status=404,
                             upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}])

    response = self.app.post(
        '/tenders/{}/agreements/some_id/documents?acc_token={}'.format(self.tender_id, self.tender_token),
        status=404,
        upload_files=[('file', 'name.doc', 'content')]
    )
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'agreement_id'}])

    response = self.app.post(
        '/tenders/{}/agreements/{}/documents?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        status=404,
        upload_files=[('invalid_value', 'name.doc', 'content')]
    )
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{u'description': u'Not Found', u'location': u'body', u'name': u'file'}])

    response = self.app.get('/tenders/some_id/agreements/some_id/documents', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}])

    response = self.app.get('/tenders/{}/agreements/some_id/documents'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'agreement_id'}])

    response = self.app.get('/tenders/some_id/agreements/some_id/documents/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}])

    response = self.app.get('/tenders/{}/agreements/some_id/documents/some_id'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'agreement_id'}])

    response = self.app.get('/tenders/{}/agreements/{}/documents/some_id'.format(self.tender_id, self.agreement_id),
                            status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}])

    response = self.app.put(
        '/tenders/some_id/agreements/some_id/documents/some_id?acc_token={}'.format(self.tender_token),
        status=404,
        upload_files=[('file', 'name.doc', 'content2')]
    )
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}])

    response = self.app.put(
        '/tenders/{}/agreements/some_id/documents/some_id?acc_token={}'.format(self.tender_id, self.tender_token),
        status=404,
        upload_files=[('file', 'name.doc', 'content2')]
    )
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'agreement_id'}])

    response = self.app.put(
        '/tenders/{}/agreements/{}/documents/some_id?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                          self.tender_token),
        status=404,
        upload_files=[('file', 'name.doc', 'content2')]
    )
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}])


# Agreement contracts
def get_tender_agreement_contracts(self):
    min_contracts_count = 3
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    agreement = response.json['data'][0]
    items_id = [i['id'] for i in agreement['items']]

    self.assertEqual(agreement['status'], 'pending')
    self.assertEqual(len(agreement['contracts']), min_contracts_count)

    response = self.app.get('/tenders/{}/agreements/{}/contracts'.format(self.tender_id, agreement['id']))
    self.assertEqual(len(response.json['data']), min_contracts_count)
    for contract in response.json['data']:
        self.assertEqual(contract['status'], 'active')
        for unit_price in contract['unitPrices']:
            self.assertNotIn('amount', unit_price['value'])
            self.assertIn(unit_price['relatedItem'], items_id)

    response = self.app.get('/tenders/{}/agreements/some_agreement_id/contracts'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'agreement_id'}])


def get_tender_agreement_contract(self):
    min_contracts_count = 3
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    agreement = response.json['data']['agreements'][0]
    contracts = agreement['contracts']
    items_id = [i['id'] for i in agreement['items']]

    self.assertEqual(agreement['status'], 'pending')
    self.assertEqual(len(agreement['contracts']), min_contracts_count)

    for contract in contracts:
        response = self.app.get('/tenders/{}/agreements/{}/contracts/{}'.format(self.tender_id, agreement['id'],
                                                                                contract['id']))
        self.assertEqual(contract, response.json['data'])
        self.assertEqual(contract['status'], 'active')
        for unit_price in contract['unitPrices']:
            self.assertNotIn('amount', unit_price['value'])
            self.assertIn(unit_price['relatedItem'], items_id)

    response = self.app.get('/tenders/{}/agreements/{}/contracts/invalid_id'.format(self.tender_id, agreement['id']),
                            status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'contract_id'}])


def patch_tender_agreement_contract(self):
    response = self.app.get(
        '/tenders/{}/agreements/{}/contracts/{}'.format(self.tender_id, self.agreement_id, self.contract_id)
    )
    contract = response.json['data']
    self.assertEqual(contract['status'], 'active')
    for unit_price in contract['unitPrices']:
        self.assertNotIn('amount', unit_price['value'])

    related_item = contract['unitPrices'][0]['relatedItem']
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     self.contract_id, self.tender_token),
        {
            "data": {
                'unitPrices': [
                    {"relatedItem": related_item, 'value': {'amount': 100}},
                    {"relatedItem": uuid4().hex, 'value': {'amount': 1}}
                ]
            }
        },
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'],
                     [{u'description': u"unitPrice.value.amount count doesn't match with contract.",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     self.contract_id, self.tender_token),
        {"data": {'unitPrices': [{"relatedItem": uuid4().hex, 'value': {'amount': 1}}]}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'],
                     [{u'description': u"All relatedItem values doesn't match with contract.",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     self.contract_id, self.tender_token),
        {"data": {'status': "unsuccessful"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], 'unsuccessful')

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     self.contract_id, self.tender_token),
        {"data": {'unitPrices': [{'value': {'amount': 60, 'currency': 'RUB', 'valueAddedTaxIncluded': False}}]}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json['errors'],
                     [{"location": "body",
                       "name": "data",
                       "description": "currency of bid should be identical to currency of value of lot"}])

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     self.contract_id, self.tender_token),
        {"data": {'unitPrices': [{'value': {'amount': 60, 'currency': 'UAH', 'valueAddedTaxIncluded': False}}]}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json['errors'],
        [{"location": "body",
          "name": "data",
          "description": "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot"}])

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     self.contract_id, self.tender_token),
        {"data": {'unitPrices': [{'value': {'amount': 60}}]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
    self.assertEqual(response.json['data']['unitPrices'][0]['value']['amount'], 60)

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     self.contract_id, self.tender_token),
        {"data": {'status': "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], 'active')
    self.assertEqual(response.json['data']['unitPrices'][0]['value']['amount'], 60)


# def patch_no_lot_agreement_contract_unit_prices(self):
#     response = self.app.post_json('/tenders', {'data': self.initial_data})
#     self.tender_id = response.json['data']['id']
#     self.tender_token = response.json['access']['token']
    
#     bids = deepcopy(self.meta_initial_bids)
#     bids[0]['value']['amount'] = 0
#     for bid in bids:
#         response = self.app.post_json(
#             '/tenders/{}/bids?acc_token={}'
#                 .format(self.tender_id, self.tender_token),
#             {'data': bid}
#         )
#     bid_id = response.json['data']['id']
    
#     self.set_status('active.awarded')
#     response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
#     agreement = response.json['data'][0]
#     contract = [c for c in agreement['contracts'] if c['bidID'] == bid_id][0]

#     response = self.app.patch_json('/tenders/{}/agreements/{}/contracts/{}?acc_token={}'
#             .format(self.tender_id, agreement['id'], contract['id'], self.tender_token),
#             {'data': {'unitPrices': [{'value': {'amount': 60}}]}},
#     )
#     self.assertEqual(response.status, '200 OK')

#     response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
#     bids = response.json['data']
#     bid_id = [b for b in bids if b['value']['amount'] == 0][0]['id']
#     contract = [c for c in agreement['contracts'] if c['bidID'] == bid_id][0]

#     response = self.app.patch_json('/tenders/{}/agreements/{}/contracts/{}?acc_token={}'
#             .format(self.tender_id, agreement['id'], contract['id'], self.tender_token),
#             {'data': {'unitPrices': [{'value': {'amount': 60}}]}},
#             status=403
#     )
#     self.assertEqual(response.status, '403 Forbidden')
#     self.assertEqual(response.json['errors'], [{
#         "location": "body",
#         "name": "data",
#         "description": "Total amount can't be greater than bid.value.amount"}]
#     )


def patch_lots_agreement_contract_unit_prices(self):
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    bid_id = response.json['data']['bids'][-1]['id']
    bid_value = response.json['data']['bids'][-1]['lotValues'][0]['value']['amount']

    self.set_status('active.awarded')
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    agreement = response.json['data'][0]
    contract = [c for c in agreement['contracts'] if c['bidID'] == bid_id][0]

    response = self.app.patch_json('/tenders/{}/agreements/{}/contracts/{}?acc_token={}'
            .format(self.tender_id, agreement['id'], contract['id'], self.tender_token),
            {'data': {'unitPrices': [{'value': {'amount': 60}}]}},
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    bids = response.json['data']
    bid_id = [b for b in bids if b['lotValues'][0]['value']['amount'] == bid_value][0]['id']
    contract = [c for c in agreement['contracts'] if c['bidID'] == bid_id][0]

    response = self.app.patch_json('/tenders/{}/agreements/{}/contracts/{}?acc_token={}'
            .format(self.tender_id, agreement['id'], contract['id'], self.tender_token),
            {'data': {'unitPrices': [{'value': {'amount': 6000}}]}},
            status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'], [{
        "location": "body",
        "name": "data",
        "description": "Total amount can't be greater than bid.lotValue.value.amount"}]
    )


def four_contracts_one_unsuccessful(self):
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    agreement = response.json['data'][0]
    self.assertEqual(agreement['status'], 'pending')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']
    self.assertEqual(tender['status'], 'active.awarded')

    # Fill 3 unitPrice.value.amount for all contracts in agreement
    response = self.app.get('/tenders/{}/agreements/{}/contracts'.format(self.tender_id, self.agreement_id))
    contracts = response.json['data']
    for contract in contracts[:-1]:
        unit_prices = contract['unitPrices']
        for unit_price in unit_prices:
            unit_price['value']['amount'] = 60
        response = self.app.patch_json(
            '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                         contract['id'], self.tender_token),
            {'data': {'unitPrices': unit_prices}}
        )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

    # Set last contract to unsuccessful
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     contracts[-1]['id'], self.tender_token),
        {'data': {'status': 'unsuccessful'}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'unsuccessful')

    tender = self.db.get(self.tender_id)
    tender['contractPeriod']['startDate'] =\
        (datetime.now() - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1)).isoformat()
    tender['contractPeriod']['clarificationsUntil'] = (datetime.now() - timedelta(days=1)).isoformat()
    self.db.save(tender)

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": agreement_period}}
    )
    self.assertEqual(response.json['data']['status'], 'active')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']
    self.assertEqual(tender['status'], 'complete')
    self.assertEqual(len([c for c in tender['agreements'][0]['contracts'] if c['status'] == 'active']), 3)
    self.assertEqual(len([c for c in tender['agreements'][0]['contracts'] if c['status'] == 'unsuccessful']), 1)

    for unit_price in tender['agreements'][0]['contracts'][-1]['unitPrices']:
        self.assertNotIn('amount', unit_price['value'])
