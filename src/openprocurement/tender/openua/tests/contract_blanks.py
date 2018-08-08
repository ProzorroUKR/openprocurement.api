# -*- coding: utf-8 -*-
from datetime import timedelta
from openprocurement.api.utils import get_now


# TenderContractResourceTest


def create_tender_contract(self):
    auth = self.app.authorization
    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.post_json('/tenders/{}/contracts'.format(
        self.tender_id),
        {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    contract = response.json['data']
    self.assertIn('id', contract)
    self.assertIn(contract['id'], response.headers['Location'])

    tender = self.db.get(self.tender_id)
    tender['contracts'][-1]["status"] = "terminated"
    self.db.save(tender)

    self.set_status('unsuccessful')

    response = self.app.post_json('/tenders/{}/contracts'.format(
        self.tender_id),
        {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}},
        status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add contract in current (unsuccessful) tender status")

    self.app.authorization = auth
    response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
        self.tender_id, contract['id'], self.tender_token), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (unsuccessful) tender status")


def patch_tender_contract_datesigned(self):
    response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
    contract = response.json['data'][0]

    self.set_status('complete', {'status': 'active.awarded'})

    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)

    response = self.app.patch_json(
        '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
        {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertIn(u"dateSigned", response.json['data'].keys())


def patch_tender_contract(self):
    response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
    contract = response.json['data'][0]

    response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
        self.tender_id, contract['id'], self.tender_token), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn("Can't sign contract before stand-still period end (", response.json['errors'][0]["description"])

    self.set_status('complete', {'status': 'active.awarded'})
    # response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
    #     self.tender_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
    # self.assertEqual(response.status, '201 Created')
    # complaint = response.json['data']
    #
    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    #
    # response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']), {"data": {"status": "active"}}, status=403)
    # self.assertEqual(response.status, '403 Forbidden')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['errors'][0]["description"], "Can't sign contract before reviewing all complaints")
    #
    # response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint['id']), {"data": {"status": "invalid", "resolution": "spam"}})
    # self.assertEqual(response.status, '200 OK')
    response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
        self.tender_id, contract['id'], self.tender_token), {"data": {"value": {"valueAddedTaxIncluded": False}}},
        status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can\'t update valueAddedTaxIncluded for contract value")
    response = self.app.patch_json(
        '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
        {"data": {"value": {"amount": 501}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Value amount should be less or equal to awarded amount (469.0) if VAT included")

    response = self.app.patch_json(
        '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
        {"data": {"value": {"amount": 238}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Value amountNet should be less or equal to amount (238.0)")

    response = self.app.patch_json(
        '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
        {"data": {"value": {"amount": 100, "amountNet": 80}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['value']['amount'], 100)
    self.assertEqual(response.json['data']['value']['amountNet'], 80)

    response = self.app.patch_json(
        '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
        {"data": {"value": {"amount": 100, "amountNet": 79.9}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Value amountNet can't be less than amount (100.0) for 20.0% (80.0) if VAT included")

    response = self.app.patch_json(
        '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
        {"data": {"value": {"amount": 238, "amountNet": 238}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['value']['amount'], 238)
    self.assertEqual(response.json['data']['value']['amountNet'], 238)

    response = self.app.patch_json(
        '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
        {"data": {"dateSigned": i['complaintPeriod']['endDate']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [{u'description': [
        u'Contract signature date should be after award complaint period end date ({})'.format(
            i['complaintPeriod']['endDate'])], u'location': u'body', u'name': u'dateSigned'}])

    one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json(
        '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
        {"data": {"dateSigned": one_hour_in_furure}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Contract signature date can't be in the future"], u'location': u'body',
         u'name': u'dateSigned'}])

    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json(
        '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
        {"data": {"dateSigned": custom_signature_date}})
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
        {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
        self.tender_id, contract['id'], self.tender_token), {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) tender status")

    response = self.app.patch_json('/tenders/{}/contracts/some_id?acc_token={}'.format(
        self.tender_id, self.tender_token), {"data": {"status": "active"}}, status=404)
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
