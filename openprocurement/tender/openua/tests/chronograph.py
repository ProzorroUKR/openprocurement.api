# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import test_lots, test_bids
from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest


class TenderSwitch0BidResourceTest(BaseTenderUAContentWebTest):

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "unsuccessful")

    def test_set_auction_period(self):
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": None}}})
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('auctionPeriod', response.json['data'])


class TenderSwitch1BidResourceTest(BaseTenderUAContentWebTest):
    initial_bids = test_bids[:1]

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "unsuccessful")


class TenderSwitchAuctionResourceTest(BaseTenderUAContentWebTest):
    initial_bids = test_bids

    def test_switch_to_auction(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active.auction")

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': response.json['data']['bids']}})
        self.assertEqual(response.json['data']["status"], "active.qualification")

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        print response.json['data']
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}})

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}})

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["status"], "unsuccessful")


class TenderLotSwitch0BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "unsuccessful")
        self.assertEqual(set([i['status'] for i in response.json['data']["lots"]]), set(["unsuccessful"]))

    def test_set_auction_period(self):
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [
            {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}
            for i in self.initial_lots
        ]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["lots"][0]['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": None}}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('auctionPeriod', response.json['data']["lots"][0])


class TenderLotSwitch1BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots
    initial_bids = test_bids[:1]

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "unsuccessful")


class TenderLotSwitchAuctionResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots
    initial_bids = test_bids

    def test_switch_to_auction(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active.auction")

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot in response.json['data']['lots']:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot['id']), {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')

        self.assertEqual(response.json['data']["status"], "active.qualification")

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        while any([i['status'] == 'pending' for i in response.json['data']]):
            award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
            self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}})
            response = self.app.get('/tenders/{}/awards'.format(self.tender_id))

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["status"], "unsuccessful")


class Tender2LotSwitch0BidResourceTest(TenderLotSwitch0BidResourceTest):
    initial_lots = 2 * test_lots


class Tender2LotSwitch1BidResourceTest(TenderLotSwitch1BidResourceTest):
    initial_lots = 2 * test_lots


class Tender2LotSwitchAuctionResourceTest(TenderLotSwitchAuctionResourceTest):
    initial_lots = 2 * test_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitch1BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitch1BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchAuctionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
