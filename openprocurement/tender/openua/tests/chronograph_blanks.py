# -*- coding: utf-8 -*-
# TenderSwitch0BidResourceTest


def set_auction_period_0bid(self):
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                   {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                   {'data': {"auctionPeriod": {"startDate": None}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('auctionPeriod', response.json['data'])
    self.assertNotIn('startDate', response.json['data']['auctionPeriod'])


# TenderSwitch1BidResourceTest


def switch_to_unsuccessful_1bid(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")


# TenderSwitchAuctionResourceTest


def switch_to_complaint(self):
    for status in ['invalid', 'resolved', 'declined']:
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': self.author_data,
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

    response = self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active.auction")
    self.assertEqual(response.json['data']["complaints"][-1]['status'], status)


def switch_to_unsuccessful(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})

    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': response.json['data']['bids']}})
    self.assertEqual(response.json['data']["status"], "active.qualification")

    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
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


def set_auction_period(self):
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    item = response.json['data']
    self.assertIn('auctionPeriod', item)
    self.assertIn('shouldStartAfter', item['auctionPeriod'])
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
    self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}})
    item = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(item['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": None}}})
    item = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('startDate', item['auctionPeriod'])
# TenderLotSwitch0BidResourceTest
# TenderLotSwitchAuctionResourceTest


# TenderLotSwitch0BidResourceTest


def switch_to_unsuccessful_lot_0bid(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")
    self.assertEqual(set([i['status'] for i in response.json['data']["lots"]]), set(["unsuccessful"]))


def set_auction_period_lot_0bid(self):
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


def switch_to_unsuccessful_lot_1bid(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")


# TnederLotSwitchAuctionResourceTest

def switch_to_auction_lot(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active.auction")


def switch_to_unsuccessful_lot(self):
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


def set_auction_period_lot(self):
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    item = response.json['data']["lots"][0]
    self.assertIn('auctionPeriod', item)
    self.assertIn('shouldStartAfter', item['auctionPeriod'])
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
    self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}} for i in self.initial_lots]}})
    item = response.json['data']["lots"][0]
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(item['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": None}} for i in self.initial_lots]}})
    item = response.json['data']["lots"][0]
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('startDate', item['auctionPeriod'])
