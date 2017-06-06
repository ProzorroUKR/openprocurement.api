# -*- coding: utf-8 -*-


# TenderComplaintResourceTest


def create_tender_complaint(self):
    response = self.app.post_json('/tenders/{}/complaints'.format(
        self.tender_id), {
        'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.test_author,
                 'status': 'claim'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']
    owner_token = response.json['access']['token']
    self.assertEqual(complaint['author']['name'], self.test_author['name'])
    self.assertIn('id', complaint)
    self.assertIn(complaint['id'], response.headers['Location'])

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], self.tender_token), {"data": {
            "status": "answered"
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'resolutionType'},
    ])

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], self.tender_token), {"data": {
            "status": "answered",
            "resolutionType": "invalid",
            "resolution": "spam 100% " * 3
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "answered")
    self.assertEqual(response.json['data']["resolutionType"], "invalid")
    self.assertEqual(response.json['data']["resolution"], "spam 100% " * 3)

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token), {"data": {
            "satisfied": True,
            "status": "resolved"
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "resolved")

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update complaint in current (resolved) status")

    self.set_status('unsuccessful')

    response = self.app.post_json('/tenders/{}/complaints'.format(
        self.tender_id),
        {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.test_author}},
        status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add complaint in current (unsuccessful) tender status")


def patch_tender_complaint(self):
    response = self.app.post_json('/tenders/{}/complaints'.format(
        self.tender_id),
        {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.test_author}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], self.tender_token), {"data": {
            "status": "cancelled",
            "cancellationReason": "reason"
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Forbidden")

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token), {"data": {
            "title": "claim title",
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["title"], "claim title")

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token), {"data": {
            "status": "claim",
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], "claim")

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], self.tender_token), {"data": {
            "resolution": "changing rules"
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["resolution"], "changing rules")

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], self.tender_token), {"data": {
            "status": "answered",
            "resolutionType": "resolved",
            "resolution": "resolution text" * 2
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "answered")
    self.assertEqual(response.json['data']["resolutionType"], "resolved")
    self.assertEqual(response.json['data']["resolution"], "resolution text" * 2)

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token), {"data": {
            "satisfied": False
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["satisfied"], False)

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token), {"data": {
            "status": "resolved"
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update complaint")

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token), {"data": {
            "status": "pending"
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "pending")

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token), {"data": {
            "status": "stopping"
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'cancellationReason'},
    ])

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token), {"data": {
            "status": "stopping",
            "cancellationReason": "reason"
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "stopping")
    self.assertEqual(response.json['data']["cancellationReason"], "reason")

    response = self.app.patch_json('/tenders/{}/complaints/some_id'.format(self.tender_id),
                                   {"data": {"status": "resolved", "resolution": "resolution text"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'complaint_id'}
    ])

    response = self.app.patch_json('/tenders/some_id/complaints/some_id',
                                   {"data": {"status": "resolved", "resolution": "resolution text"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    response = self.app.get('/tenders/{}/complaints/{}'.format(self.tender_id, complaint['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "stopping")
    self.assertEqual(response.json['data']["cancellationReason"], "reason")
    self.assertEqual(response.json['data']["resolutionType"], "resolved")
    self.assertEqual(response.json['data']["resolution"], "resolution text" * 2)

    response = self.app.post_json('/tenders/{}/complaints'.format(
        self.tender_id),
        {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.test_author}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']
    owner_token = response.json['access']['token']

    self.set_status('complete')

    response = self.app.patch_json(
        '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token), {"data": {
            "status": "claim",
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update complaint in current (complete) tender status")


def review_tender_complaint(self):
    for status in ['invalid', 'satisfied', 'declined']:
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': self.test_author,
            'status': 'pending'
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']

        self.app.authorization = ('Basic', ('reviewer', ''))
        response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint['id']), {"data": {
            "decision": '{} complaint'.format(status)
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["decision"], '{} complaint'.format(status))

        if status != "invalid":
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint['id']),
                                           {"data": {
                                               "status": "accepted"
                                           }})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']["status"], "accepted")

            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint['id']),
                                           {"data": {
                                               "decision": 'accepted:{} complaint'.format(status)
                                           }})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']["decision"], 'accepted:{} complaint'.format(status))

        response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint['id']), {"data": {
            "status": status
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], status)


# TenderLotAwardComplaintResourceTest


def create_tender_lot_complaint(self):
    response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), {'data': {
        'title': 'complaint title',
        'description': 'complaint description',
        'author': self.test_author,
        'relatedLot': self.initial_lots[0]['id'],
        'status': 'claim'
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']
    owner_token = response.json['access']['token']
    self.assertEqual(complaint['author']['name'], self.test_author['name'])
    self.assertIn('id', complaint)
    self.assertIn(complaint['id'], response.headers['Location'])

    response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], self.tender_token), {"data": {
        "status": "answered"
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'resolutionType'},
    ])

    response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], self.tender_token), {"data": {
        "status": "answered",
        "resolutionType": "invalid",
        "resolution": "spam 100% " * 3
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "answered")
    self.assertEqual(response.json['data']["resolutionType"], "invalid")
    self.assertEqual(response.json['data']["resolution"], "spam 100% " * 3)

    response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token), {"data": {
        "satisfied": True,
        "status": "resolved"
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "resolved")

    response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], owner_token), {"data": {"status": "cancelled", "cancellationReason": "reason"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update complaint in current (resolved) status")

    self.set_status('unsuccessful')

    response = self.app.post_json('/tenders/{}/complaints'.format(
        self.tender_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.test_author}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add complaint in current (unsuccessful) tender status")


# TenderComplaintDocumentResourceTest


def put_tender_complaint_document(self):
    response = self.app.post('/tenders/{}/complaints/{}/documents?acc_token={}'.format(
        self.tender_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/tenders/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token),
                            status=404,
                            upload_files=[('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/tenders/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.complaint_id, doc_id, self.tender_token), upload_files=[('file', 'name.doc', 'content2')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")

    response = self.app.put('/tenders/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/complaints/{}/documents/{}?{}'.format(
        self.tender_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content2')

    response = self.app.get('/tenders/{}/complaints/{}/documents/{}'.format(
        self.tender_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put('/tenders/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/complaints/{}/documents/{}?{}'.format(
        self.tender_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content3')

    response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.complaint_id, self.complaint_owner_token), {"data": {
        "status": "pending",
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], "pending")

    response = self.app.put('/tenders/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token), 'content', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('complete')

    response = self.app.put('/tenders/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")


def patch_tender_complaint_document(self):
    response = self.app.post('/tenders/{}/complaints/{}/documents?acc_token={}'.format(
        self.tender_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json('/tenders/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.complaint_id, doc_id, self.tender_token), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")

    response = self.app.patch_json('/tenders/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get('/tenders/{}/complaints/{}/documents/{}'.format(
        self.tender_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])

    response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.complaint_id, self.complaint_owner_token), {"data": {
        "status": "pending",
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], "pending")

    response = self.app.patch_json('/tenders/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description2"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["description"], "document description2")

    self.set_status('complete')

    response = self.app.patch_json('/tenders/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")
