# -*- coding: utf-8 -*-
from datetime import timedelta

from openprocurement.api.utils import get_now

# TenderAgreementResourceTest


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


def create_tender_agreement(self):
    auth = self.app.authorization
    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.post_json('/tenders/{}/agreements'.format(
        self.tender_id),
        {'data': {'title': 'agreement title', 'description': 'agreement description', 'awardID': self.award_id}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    agreement = response.json['data']
    self.assertIn('id', agreement)
    self.assertIn(agreement['id'], response.headers['Location'])

    tender = self.db.get(self.tender_id)
    tender['agreements'][-1]["status"] = "terminated"
    self.db.save(tender)

    self.set_status('unsuccessful')

    response = self.app.post_json('/tenders/{}/agreements'.format(
        self.tender_id),
        {'data': {'title': 'agreement title', 'description': 'agreement description', 'awardID': self.award_id}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add agreement in current (unsuccessful) tender status")

    self.app.authorization = auth
    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active"}},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update agreement in current (unsuccessful) tender status")


def create_tender_agreement_invalid(self):
    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.post_json(
        '/tenders/some_id/agreements',
        {'data': {'title': 'agreement title', 'description': 'agreement description', 'awardID': self.award_id}},
        status=404
    )
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}])

    request_path = '/tenders/{}/agreements'.format(self.tender_id)

    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{
            u'description':
                u"Content-Type header should be one of ['application/json']",
                u'location': u'header',
                u'name': u'Content-Type'
        }]
    )

    response = self.app.post(request_path, 'data', content_type='application/json', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'No JSON object could be decoded', u'location': u'body', u'name': u'data'}])

    response = self.app.post_json(request_path, 'data', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Data not available', u'location': u'body', u'name': u'data'}])

    response = self.app.post_json(request_path, {'not_data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Data not available', u'location': u'body', u'name': u'data'}])

    response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Rogue field', u'location': u'body', u'name': u'invalid_field'}])

    response = self.app.post_json(request_path, {'data': {'awardID': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{u'description': [u'awardID should be one of awards'], u'location': u'body', u'name': u'awardID'}]
    )


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


def get_tender_agreement(self):
    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.post_json(
        '/tenders/{}/agreements'.format(self.tender_id),
        {'data': {'title': 'agreement title', 'description': 'agreement description', 'awardID': self.award_id}}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    agreement = response.json['data']

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/agreements/{}'.format(self.tender_id, agreement['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], agreement)

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
    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.post_json(
        '/tenders/{}/agreements'.format(self.tender_id),
        {'data': {'title': 'agreement title', 'description': 'agreement description', 'awardID': self.award_id}}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    agreement = response.json['data']

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][-1], agreement)

    response = self.app.get('/tenders/some_id/agreements', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}])


def patch_tender_agreement_datesigned(self):
    response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
    agreement = response.json['data'][0]

    self.set_status('complete', {'status': 'active.awarded'})

    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)

    response = self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement['id'], self.tender_token),
        {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertIn(u"dateSigned", response.json['data'].keys())


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
