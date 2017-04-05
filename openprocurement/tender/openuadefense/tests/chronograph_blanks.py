# -*- coding: utf-8 -*-

# TenderSwitch1BidResourceTest
def not_switch_to_unsuccessful(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active.qualification")


# TenderSwitchAuctionResourceTest
def switch_to_auction(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active.auction")


# TenderLotSwitch0BidResourceTest
def without_bids_switch_to_unsuccessful(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")
    self.assertEqual(set([i['status'] for i in response.json['data']["lots"]]), set(["unsuccessful"]))


def without_bids_set_auction_period(self):
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [
        {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}
        for i in self.initial_lots
    ]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["lots"][0]['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": None}}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('auctionPeriod', response.json['data']["lots"][0])
    self.assertNotIn('startDate', response.json['data']["lots"][0]['auctionPeriod'])


# TenderLotSwitch1BidResourceTest
def switch_to_qualification(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active.qualification")
