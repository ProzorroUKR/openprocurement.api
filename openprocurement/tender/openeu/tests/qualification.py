# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import test_bids
from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest


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



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderQualificationResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
