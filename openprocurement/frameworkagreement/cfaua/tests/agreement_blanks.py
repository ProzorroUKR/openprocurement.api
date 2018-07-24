# -*- coding: utf-8 -*-
from datetime import timedelta
from uuid import uuid4

from iso8601 import parse_date
from mock import patch
from openprocurement.api.utils import get_now


# TenderAgreementResourceTest

def get_tender_agreement(self):
    agreement = self.app.app.registry.db.get(self.tender_id)['agreements'][0]

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


@patch('openprocurement.frameworkagreement.cfaua.models.submodels.agreement.get_now')
@patch('openprocurement.frameworkagreement.cfaua.views.agreement.get_now')
@patch('openprocurement.frameworkagreement.cfaua.validation.get_now')
def patch_tender_agreement_datesigned(self, validation_time, view_time, model_time):
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    agreement = response.json['data'][0]
    self.assertEqual(agreement['status'], 'pending')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']
    self.assertEqual(tender['status'], 'active.awarded')

    # Time configuration
    validation_time.return_value = get_now()
    view_time.return_value = get_now()
    model_time.return_value = get_now()

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'],
        [{
            "location": "body",
            "name": "data",
            "description": "Can't sign agreement before stand-still period end ({})".format(
                tender['awardPeriod']['endDate']
            )
        }]
    )

    # Time configuration
    validation_time.return_value = parse_date(tender['awardPeriod']['endDate'])
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active"}},
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

    # Income rules:
    # All agreement.contracts.unitprices.value.amount filled.
    # response = self.app.patch_json(
    #     '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
    #     {"data": {"status": "active"}},
    #     status=422
    # )
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(
    #     response.json['errors'],
    #     [{
    #         "location": "body",
    #         "name": "agreements",
    #         "description": [{
    #             "dateSigned": [
    #                 "Agreement signature date should be after award complaint period end date ({})".format(
    #                     tender['awardPeriod']['endDate']
    #                 )
    #             ]
    #         }]
    #     }]
    # )

    # Move to separated test
    # # Time configuration
    # view_time.return_value = parse_date(tender['awardPeriod']['endDate']) + timedelta(days=1)
    # model_time.return_value = parse_date(tender['awardPeriod']['endDate']) + timedelta(days=2)
    # response = self.app.patch_json(
    #     '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
    #     {"data": {"status": "active"}}
    # )
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['data']["status"], "active")
    # self.assertIn(u"dateSigned", response.json['data'].keys())

def agreement_termination(self):
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    agreement = response.json['data'][0]
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "terminated"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update agreement status")


# def create_tender_agreement(self):
#     auth = self.app.authorization
#     self.app.authorization = ('Basic', ('token', ''))
#     response = self.app.post_json('/tenders/{}/agreements'.format(
#         self.tender_id),
#         {'data': {'title': 'agreement title', 'description': 'agreement description', 'awardID': self.award_id}})
#     self.assertEqual(response.status, '201 Created')
#     self.assertEqual(response.content_type, 'application/json')
#     agreement = response.json['data']
#     self.assertIn('id', agreement)
#     self.assertIn(agreement['id'], response.headers['Location'])

#     tender = self.db.get(self.tender_id)
#     tender['agreements'][-1]["status"] = "terminated"
#     self.db.save(tender)

#     self.set_status('unsuccessful')

#     response = self.app.post_json('/tenders/{}/agreements'.format(
#         self.tender_id),
#         {'data': {'title': 'agreement title', 'description': 'agreement description', 'awardID': self.award_id}},
#         status=403
#     )
#     self.assertEqual(response.status, '403 Forbidden')
#     self.assertEqual(response.content_type, 'application/json')
#     self.assertEqual(response.json['errors'][0]["description"],
#                      "Can't add agreement in current (unsuccessful) tender status")

#     self.app.authorization = auth
#     response = self.app.patch_json(
#         '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
#         {"data": {"status": "active"}},
#         status=403
#     )
#     self.assertEqual(response.status, '403 Forbidden')
#     self.assertEqual(response.content_type, 'application/json')
#     self.assertEqual(response.json['errors'][0]["description"],
#                      "Can't update agreement in current (unsuccessful) tender status")


# def create_tender_agreement_invalid(self):
#     self.app.authorization = ('Basic', ('token', ''))
#     response = self.app.post_json(
#         '/tenders/some_id/agreements',
#         {'data': {'title': 'agreement title', 'description': 'agreement description', 'awardID': self.award_id}},
#         status=404
#     )
#     self.assertEqual(response.status, '404 Not Found')
#     self.assertEqual(response.content_type, 'application/json')
#     self.assertEqual(response.json['status'], 'error')
#     self.assertEqual(response.json['errors'],
#                      [{u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}])

#     request_path = '/tenders/{}/agreements'.format(self.tender_id)

#     response = self.app.post(request_path, 'data', status=415)
#     self.assertEqual(response.status, '415 Unsupported Media Type')
#     self.assertEqual(response.content_type, 'application/json')
#     self.assertEqual(response.json['status'], 'error')
#     self.assertEqual(
#         response.json['errors'],
#         [{
#             u'description':
#                 u"Content-Type header should be one of ['application/json']",
#                 u'location': u'header',
#                 u'name': u'Content-Type'
#         }]
#     )

#     response = self.app.post(request_path, 'data', content_type='application/json', status=422)
#     self.assertEqual(response.status, '422 Unprocessable Entity')
#     self.assertEqual(response.content_type, 'application/json')
#     self.assertEqual(response.json['status'], 'error')
#     self.assertEqual(response.json['errors'],
#                      [{u'description': u'No JSON object could be decoded', u'location': u'body', u'name': u'data'}])

#     response = self.app.post_json(request_path, 'data', status=422)
#     self.assertEqual(response.status, '422 Unprocessable Entity')
#     self.assertEqual(response.content_type, 'application/json')
#     self.assertEqual(response.json['status'], 'error')
#     self.assertEqual(response.json['errors'],
#                      [{u'description': u'Data not available', u'location': u'body', u'name': u'data'}])

#     response = self.app.post_json(request_path, {'not_data': {}}, status=422)
#     self.assertEqual(response.status, '422 Unprocessable Entity')
#     self.assertEqual(response.content_type, 'application/json')
#     self.assertEqual(response.json['status'], 'error')
#     self.assertEqual(response.json['errors'],
#                      [{u'description': u'Data not available', u'location': u'body', u'name': u'data'}])

#     response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
#     self.assertEqual(response.status, '422 Unprocessable Entity')
#     self.assertEqual(response.content_type, 'application/json')
#     self.assertEqual(response.json['status'], 'error')
#     self.assertEqual(response.json['errors'],
#                      [{u'description': u'Rogue field', u'location': u'body', u'name': u'invalid_field'}])

#     response = self.app.post_json(request_path, {'data': {'awardID': 'invalid_value'}}, status=422)
#     self.assertEqual(response.status, '422 Unprocessable Entity')
#     self.assertEqual(response.content_type, 'application/json')
#     self.assertEqual(response.json['status'], 'error')
#     self.assertEqual(
#         response.json['errors'],
#         [{u'description': [u'awardID should be one of awards'], u'location': u'body', u'name': u'awardID'}]
#     )


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

    tender = self.db.get(self.tender_id)
    tender['agreements'][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.post(
        '/tenders/{}/agreements/{}/documents?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                  self.tender_token),
        upload_files=[('file', 'name.doc', 'content')],
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current agreement status")

    self.set_status('{}'.format(self.forbidden_agreement_document_modification_actions_status))

    response = self.app.post(
        '/tenders/{}/agreements/{}/documents?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                  self.tender_token),
        upload_files=[('file', 'name.doc', 'content')],
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add document in current ({}) tender status".format(
                         self.forbidden_contract_document_modification_actions_status))


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

    tender = self.db.get(self.tender_id)
    tender['agreements'][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.put(
        '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(self.tender_id, self.agreement_id, doc_id,
                                                                     self.tender_token),
        upload_files=[('file', 'name.doc', 'content3')],
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current agreement status")

    self.set_status('{}'.format(self.forbidden_agreement_document_modification_actions_status))

    response = self.app.put(
        '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(self.tender_id, self.agreement_id, doc_id,
                                                                     self.tender_token),
        upload_files=[('file', 'name.doc', 'content3')],
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update document in current ({}) tender status".format(
                         self.forbidden_contract_document_modification_actions_status))


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

    tender = self.db.get(self.tender_id)
    tender['agreements'][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(self.tender_id, self.agreement_id, doc_id,
                                                                     self.tender_token),
        {"data": {"description": "document description"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current agreement status")

    self.set_status('{}'.format(self.forbidden_agreement_document_modification_actions_status))

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(self.tender_id, self.agreement_id, doc_id,
                                                                     self.tender_token),
        {"data": {"description": "document description"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update document in current ({}) tender status".format(
                         self.forbidden_contract_document_modification_actions_status))









def patch_tender_agreement(self):
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    agreement = response.json['data'][0]

    fake_agreementID = "myselfID"
    fake_items_data = [{"description": "New Description"}]
    fake_suppliers_data = [{"name": "New Name"}]

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"agreementID": fake_agreementID, "items": fake_items_data, "suppliers": fake_suppliers_data}}
    )

    response = self.app.get('/tenders/{}/agreements/{}'.format(self.tender_id, agreement['id']))
    self.assertNotEqual(fake_agreementID, response.json['data']['agreementID'])
    self.assertNotEqual(fake_items_data, response.json['data']['items'])
    self.assertNotEqual(fake_suppliers_data, response.json['data']['suppliers'])

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"value": {"currency": "USD"}}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"], "Can\'t update currency for agreement value")

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": False}}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can\'t update valueAddedTaxIncluded for agreement value")

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"value": {"amount": 501}}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Value amount should be less or equal to awarded amount (500.0)")

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"value": {"amount": 238}}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['value']['amount'], 238)

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn("Can't sign agreement before stand-still period end (", response.json['errors'][0]["description"])

    self.set_status('complete', {'status': 'active.awarded'})

    token = self.initial_bids_tokens[self.initial_bids[0]['id']]
    response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
        self.tender_id, self.award_id, token),
        {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.supplier_info}})
    self.assertEqual(response.status, '201 Created')
    complaint = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'],
                                                                  owner_token), {"data": {"status": "pending"}})
    self.assertEqual(response.status, '200 OK')

    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"dateSigned": i['complaintPeriod']['endDate']}},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [{u'description': [
        u'Agreement signature date should be after award complaint period end date ({})'.format(
            i['complaintPeriod']['endDate'])], u'location': u'body', u'name': u'dateSigned'}])

    one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"dateSigned": one_hour_in_furure}},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Agreement signature date can't be in the future"], u'location': u'body',
         u'name': u'dateSigned'}])

    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"dateSigned": custom_signature_date}}
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't sign agreement before reviewing all complaints")

    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'],
                                                                  owner_token),
        {"data": {"status": "stopping", "cancellationReason": "reason"}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "stopping")

    authorization = self.app.authorization
    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint['id']),
        {'data': {'status': 'stopped'}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], "stopped")

    self.app.authorization = authorization
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {
            "data": {
                "value": {"amount": 232},
                "agreementID": "myselfID",
                "title": "New Title",
                "items": [{"description": "New Description"}],
                "suppliers": [{"name": "New Name"}]
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
    self.assertEqual(response.json['data']["value"]['amount'], 238)


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


def patch_tender_agreement_contract_unitprices(self):
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
        {"data": {'unitPrices': [{'value': {'amount': 100}}]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
    self.assertEqual(response.json['data']['unitPrices'][0]['value']['amount'], 100)

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     self.contract_id, self.tender_token),
        {"data": {'unitPrices': [{"relatedItem": related_item, 'value': {'amount': 101}}]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
    self.assertEqual(response.json['data']['unitPrices'][0]['value']['amount'], 101)

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     self.contract_id, self.tender_token),
        {"data": {'status': "active"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'],
                     [{u'description': u"Total amount can't be greater than bid.value.amount",
                       u'location': u'body',
                       u'name': u'data'}])
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.agreement_id,
                                                                     self.contract_id, self.tender_token),
        {
            "data": {
                'status': "active",
                'unitPrices': [{'relatedItem': related_item, 'value': {'amount': 60}}]
            }
        }
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], 'active')
    self.assertEqual(response.json['data']['unitPrices'][0]['value']['amount'], 60)
