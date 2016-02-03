# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest, test_bids


class TenderQualificationResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'  # 'active.pre-qualification' status sets in setUp
    initial_bids = test_bids

    def setUp(self):
        super(TenderQualificationResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={'status': 'active.tendering'})

        # simulate chronograph tick
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')
        self.app.authorization = auth

    def test_post_tender_qualifications(self):
        response = self.app.post_json('/tenders/{}/qualifications'.format(self.tender_id), {"data": {}}, status=405)
        self.assertEqual(response.status, '405 Method Not Allowed')

        data = {"bidID": "some_id", "status": "pending"}
        response = self.app.post_json('/tenders/{}/qualifications'.format(self.tender_id), {"data": data}, status=405)
        self.assertEqual(response.status, '405 Method Not Allowed')

        data = {"bidID": "some_id", "status": "pending", "id": "12345678123456781234567812345678"}
        response = self.app.post_json('/tenders/{}/qualifications'.format(self.tender_id), {"data": data}, status=405)
        self.assertEqual(response.status, '405 Method Not Allowed')

    def test_get_tender_qualifications(self):
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        self.assertEqual(len(qualifications), 2)

        response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
        self.assertEqual(response.content_type, 'application/json')
        qualification_bid_ids = [q['bidID'] for q in qualifications]
        for bid in response.json['data']:
            self.assertIn(bid['id'], qualification_bid_ids)
            qualification_bid_ids.remove(bid['id'])

    def test_patch_tender_qualifications(self):
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

        response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(self.tender_id, qualifications[1]['id']),
                                      {"data": {'status': 'active'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(self.tender_id, qualifications[0]['id']),
                                      {"data": {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'cancelled')


class TenderQualificationDocumentResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids

    def setUp(self):
        super(TenderQualificationDocumentResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={'status': 'active.tendering'})

        # simulate chronograph tick
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        self.app.authorization = auth  # ('Basic', ('broker', ''))
        # list qualifications
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        self.qualifications = response.json['data']
        self.assertEqual(len(self.qualifications), 2)

    def test_not_found(self):
        response = self.app.post('/tenders/some_id/qualifications/some_id/documents', status=404, upload_files=[
                                 ('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post('/tenders/{}/qualifications/some_id/documents'.format(self.tender_id), status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'qualification_id'}
        ])

        response = self.app.post('/tenders/{}/qualifications/{}/documents'.format(self.tender_id, self.qualifications[0]['id']),
                                 status=404, upload_files=[('invalid_value', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.get('/tenders/some_id/qualifications/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/qualifications/some_id/documents'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'qualification_id'}
        ])

        response = self.app.get('/tenders/some_id/qualifications/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/qualifications/some_id/documents/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'qualification_id'}
        ])

        response = self.app.get('/tenders/{}/qualifications/{}/documents/some_id'.format(self.tender_id, self.qualifications[0]['id']), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        response = self.app.put('/tenders/some_id/qualifications/some_id/documents/some_id', status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.put('/tenders/{}/qualifications/some_id/documents/some_id'.format(self.tender_id), status=404, upload_files=[
                                ('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'qualification_id'}
        ])

        response = self.app.put('/tenders/{}/qualifications/{}/documents/some_id'.format(
            self.tender_id, self.qualifications[0]['id']), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

        self.app.authorization = ('Basic', ('invalid', ''))
        response = self.app.put('/tenders/{}/qualifications/{}/documents/some_id'.format(
            self.tender_id, self.qualifications[0]['id']), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_qualification_document(self):
        response = self.app.post('/tenders/{}/qualifications/{}/documents'.format(
            self.tender_id, self.qualifications[0]['id']), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]

        # qualifications are public
        response = self.app.get('/tenders/{}/qualifications/{}/documents'.format(self.tender_id, self.qualifications[0]['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/qualifications/{}/documents?all=true'.format(self.tender_id, self.qualifications[0]['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/qualifications/{}/documents/{}?download=some_id'.format(
            self.tender_id, self.qualifications[0]['id'], doc_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/qualifications/{}/documents/{}?{}'.format(
            self.tender_id, self.qualifications[0]['id'], doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/qualifications/{}/documents/{}'.format(
            self.tender_id, self.qualifications[0]['id'], doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

    def test_put_qualification_document(self):
        response = self.app.post('/tenders/{}/qualifications/{}/documents'.format(
            self.tender_id, self.qualifications[0]['id']), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/qualifications/{}/documents/{}'.format(self.tender_id, self.qualifications[0]['id'],
                                                                                    doc_id),
                                status=404, upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/qualifications/{}/documents/{}'.format(
            self.tender_id, self.qualifications[0]['id'], doc_id), upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/qualifications/{}/documents/{}?{}'.format(
            self.tender_id, self.qualifications[0]['id'], doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/qualifications/{}/documents/{}'.format(
            self.tender_id, self.qualifications[0]['id'], doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.put('/tenders/{}/qualifications/{}/documents/{}'.format(
            self.tender_id, self.qualifications[0]['id'], doc_id), 'content3', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/qualifications/{}/documents/{}?{}'.format(
            self.tender_id, self.qualifications[0]['id'], doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

    def test_patch_qualification_document(self):
        response = self.app.post('/tenders/{}/qualifications/{}/documents'.format(
            self.tender_id, self.qualifications[0]['id']), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/qualifications/{}/documents/{}'.format(self.tender_id, self.qualifications[0]['id'], doc_id), {"data": {
            "documentOf": "lot"
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedItem'},
        ])

        response = self.app.patch_json('/tenders/{}/qualifications/{}/documents/{}'.format(self.tender_id, self.qualifications[0]['id'], doc_id), {"data": {
            "documentOf": "lot",
            "relatedItem": '0' * 32
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
        ])

        response = self.app.patch_json('/tenders/{}/qualifications/{}/documents/{}'.format(self.tender_id, self.qualifications[0]['id'], doc_id), {"data": {"description": "document description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        response = self.app.get('/tenders/{}/qualifications/{}/documents/{}'.format(
            self.tender_id, self.qualifications[0]['id'], doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])

    def test_create_qualification_document_in_active_status(self):
        response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(
            self.tender_id, self.qualifications[0]['id']), {'data': {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.post('/tenders/{}/qualifications/{}/documents'.format(
            self.tender_id, self.qualifications[0]['id']), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderQualificationResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
