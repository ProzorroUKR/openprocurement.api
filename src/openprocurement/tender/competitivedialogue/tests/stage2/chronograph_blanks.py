# -*- coding: utf-8 -*-
# TenderStage2EUSwitchUnsuccessfulResourceTest


def switch_to_unsuccessful_eu(self):
    self.set_status('active.pre-qualification', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")


# TenderStage2UA2LotSwitch0BidResourceTest


def set_auction_period_2_lot_0_bid_ua(self):
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                   {'data': {'lots': [{'auctionPeriod': {'startDate': '9999-01-01T00:00:00+00:00'}}
                                                      for i in self.lots]}
                                    })
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["lots"][0]['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                   {'data': {'lots': [{'auctionPeriod': {'startDate': None}},
                                                      {'auctionPeriod': {'startDate': None}}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('auctionPeriod', response.json['data']["lots"][0])
    self.assertNotIn('startDate', response.json['data']["lots"][0]['auctionPeriod'])
