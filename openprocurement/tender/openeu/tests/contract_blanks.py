# -*- coding: utf-8 -*-
from datetime import timedelta

from openprocurement.api.utils import get_now

# TenderContractResourceTest


def contract_termination(self):
    response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
    contract = response.json['data'][0]
    response = self.app.patch_json(
        '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
        {"data": {"status": "terminated"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update contract status")


def patch_tender_contract(self):
    response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
    contract = response.json['data'][0]

    fake_contractID = "myselfID"
    fake_items_data = [{"description": "New Description"}]
    fake_suppliers_data = [{"name": "New Name"}]

    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']), {
        "data": {"contractID": fake_contractID, "items": fake_items_data, "suppliers": fake_suppliers_data}})

    response = self.app.get('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']))
    self.assertNotEqual(fake_contractID, response.json['data']['contractID'])
    self.assertNotEqual(fake_items_data, response.json['data']['items'])
    self.assertNotEqual(fake_suppliers_data, response.json['data']['suppliers'])

    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"value": {"currency": "USD"}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"], "Can\'t update currency for contract value")

    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"value": {"valueAddedTaxIncluded": False}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can\'t update valueAddedTaxIncluded for contract value")

    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"value": {"amount": 501}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Value amount should be less or equal to awarded amount (500.0)")

    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"value": {"amount": 238}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['value']['amount'], 238)

    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn("Can't sign contract before stand-still period end (", response.json['errors'][0]["description"])

    self.set_status('complete', {'status': 'active.awarded'})

    response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
        self.tender_id, self.award_id),
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

    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"dateSigned": i['complaintPeriod']['endDate']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [{u'description': [
        u'Contract signature date should be after award complaint period end date ({})'.format(
            i['complaintPeriod']['endDate'])], u'location': u'body', u'name': u'dateSigned'}])

    one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"dateSigned": one_hour_in_furure}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Contract signature date can't be in the future"], u'location': u'body',
         u'name': u'dateSigned'}])

    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"dateSigned": custom_signature_date}})
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't sign contract before reviewing all complaints")

    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'],
                                                                  owner_token), {"data": {
            "status": "stopping",
            "cancellationReason": "reason"
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "stopping")

    authorization = self.app.authorization
    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint['id']), {'data': {
            'status': 'stopped'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], "stopped")

    self.app.authorization = authorization
    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(
        self.tender_id, contract['id']), {"data": {
        "value": {"amount": 232},
        "contractID": "myselfID",
        "title": "New Title",
        "items": [{"description": "New Description"}],
        "suppliers": [{"name": "New Name"}]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) tender status")

    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) tender status")

    response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                   {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) tender status")

    response = self.app.patch_json('/tenders/{}/contracts/some_id'.format(self.tender_id),
                                   {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'contract_id'}
    ])

    response = self.app.patch_json('/tenders/some_id/contracts/some_id', {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    response = self.app.get('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertEqual(response.json['data']["value"]['amount'], 238)
