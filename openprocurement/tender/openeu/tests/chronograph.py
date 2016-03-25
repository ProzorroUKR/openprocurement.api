# -*- coding: utf-8 -*-
import unittest

# from openprocurement.api.tests.base import BaseTenderWebTest, test_lots, test_bids
from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest, test_bids
from copy import deepcopy


class TenderSwitchPreQualificationResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids

    def test_switch_to_auction(self):
        response = self.set_status('active.pre-qualification', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active.pre-qualification")



class TenderSwitchAuctionResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.pre-qualification.stand-still'
    initial_bids = test_bids

    def test_switch_to_auction(self):
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                          {"data": {'status': 'active'}})

        response = self.set_status('active.auction', {'status': 'active.pre-qualification.stand-still'})

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active.auction")

class TenderSwitchUnsuccessfulResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'

    def test_switch_to_unsuccessful(self):
        self.set_status('active.pre-qualification', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "unsuccessful")

#
# class TenderLotSwitchQualificationResourceTest(BaseTenderWebTest):
#     initial_status = 'active.tendering'
#     initial_lots = test_lots
#     initial_bids = test_bids[:1]
#
#     def test_switch_to_qualification(self):
#         response = self.set_status('active.auction', {'status': self.initial_status})
#         self.app.authorization = ('Basic', ('chronograph', ''))
#         response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
#         self.assertEqual(response.status, '200 OK')
#         self.assertEqual(response.content_type, 'application/json')
#         self.assertEqual(response.json['data']["status"], "active.qualification")
#         self.assertEqual(len(response.json['data']["awards"]), 1)


# class TenderLotSwitchAuctionResourceTest(BaseTenderWebTest):
#     initial_status = 'active.tendering'
#     initial_lots = test_lots
#     initial_bids = test_bids
#
#     def test_switch_to_auction(self):
#         response = self.set_status('active.auction', {'status': self.initial_status})
#         self.app.authorization = ('Basic', ('chronograph', ''))
#         response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
#         self.assertEqual(response.status, '200 OK')
#         self.assertEqual(response.content_type, 'application/json')
#         self.assertEqual(response.json['data']["status"], "active.auction")


# class TenderLotSwitchUnsuccessfulResourceTest(BaseTenderWebTest):
#     initial_status = 'active.tendering'
#     initial_lots = test_lots
#
#     def test_switch_to_unsuccessful(self):
#         response = self.set_status('active.auction', {'status': self.initial_status})
#         self.app.authorization = ('Basic', ('chronograph', ''))
#         response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
#         self.assertEqual(response.status, '200 OK')
#         self.assertEqual(response.content_type, 'application/json')
#         self.assertEqual(response.json['data']["status"], "unsuccessful")
#         self.assertEqual(set([i['status'] for i in response.json['data']["lots"]]), set(["unsuccessful"]))


class TenderAuctionPeriodResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'

    def test_set_auction_period(self):
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": None}}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('auctionPeriod', response.json['data'])


# class TenderLotAuctionPeriodResourceTest(BaseTenderWebTest):
#     initial_status = 'active.tendering'
#     initial_lots = test_lots
#
#     def test_set_auction_period(self):
#         self.app.authorization = ('Basic', ('chronograph', ''))
#         response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}]}})
#         self.assertEqual(response.status, '200 OK')
#         self.assertEqual(response.json['data']["lots"][0]['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')
#
#         response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": None}}]}})
#         self.assertEqual(response.status, '200 OK')
#         self.assertNotIn('auctionPeriod', response.json['data']["lots"][0])


class TenderComplaintSwitchResourceTest(BaseTenderContentWebTest):
    initial_bids = test_bids

    def test_switch_to_complaint(self):
        user_data = deepcopy(self.initial_data["procuringEntity"])
        for status in ['invalid', 'resolved', 'declined']:
            response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), {'data': {
                'title': 'complaint title',
                'description': 'complaint description',
                'author': user_data,
                'status': 'claim'
            }})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.json['data']['status'], 'claim')
            complaint = response.json['data']

            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], self.tender_token), {"data": {
                "status": "answered",
                "resolution": status * 4,
                "resolutionType": status
            }})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']["status"], "answered")
            self.assertEqual(response.json['data']["resolutionType"], status)

        response = self.set_status('active.pre-qualification', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active.pre-qualification")
        self.assertEqual(response.json['data']["complaints"][-1]['status'], status)


# class TenderLotComplaintSwitchResourceTest(TenderComplaintSwitchResourceTest):
#     initial_lots = test_lots
#
# class TenderLotAwardComplaintSwitchResourceTest(TenderAwardComplaintSwitchResourceTest):
#     initial_lots = test_lots
#
#     def setUp(self):
#         super(TenderAwardComplaintSwitchResourceTest, self).setUp()
#         # Create award
#         response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id), {'data': {
#             'suppliers': [self.initial_data["procuringEntity"]],
#             'status': 'pending',
#             'bid_id': self.initial_bids[0]['id'],
#             'lotID': self.initial_bids[0]['lotValues'][0]['relatedLot']
#         }})
#         award = response.json['data']
#         self.award_id = award['id']


def suite():
    suite = unittest.TestSuite()
    # suite.addTest(unittest.makeSuite(TenderAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintSwitchResourceTest))
    # suite.addTest(unittest.makeSuite(TenderLotAwardComplaintSwitchResourceTest))
    # suite.addTest(unittest.makeSuite(TenderLotComplaintSwitchResourceTest))
    # suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    # suite.addTest(unittest.makeSuite(TenderLotSwitchQualificationResourceTest))
    # suite.addTest(unittest.makeSuite(TenderLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchUnsuccessfulResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
