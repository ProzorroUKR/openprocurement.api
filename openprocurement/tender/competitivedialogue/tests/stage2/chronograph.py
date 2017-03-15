# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_bids,
    author,
    test_lots
)

test_tender_bids = deepcopy(test_bids[:2])
for test_bid in test_tender_bids:
    test_bid['tenderers'] = [author]


class TenderStage2EUSwitchPreQualificationResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_tender_bids

    def test_switch_to_auction(self):
        self.set_status('active.pre-qualification', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active.pre-qualification")


class TenderStage2EUSwitchAuctionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.pre-qualification.stand-still'
    initial_bids = test_tender_bids

    def test_switch_to_auction(self):
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        for qualification in qualifications:
            self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                    qualification['id'],
                                                                                    self.tender_token),
                                {'data': {'status': 'active'}})

        self.set_status('active.auction', {'status': 'active.pre-qualification.stand-still'})

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active.auction")


class TenderStage2EUSwitchUnsuccessfulResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'

    def test_switch_to_unsuccessful(self):
        self.set_status('active.pre-qualification', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "unsuccessful")


class TenderStage2EUAuctionPeriodResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'

    def test_set_auction_period(self):
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {'data': {"auctionPeriod": {"startDate": None}}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('auctionPeriod', response.json['data'])


class TenderStage2EUComplaintSwitchResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_bids = test_tender_bids

    def test_switch_to_complaint(self):
        user_data = deepcopy(author)
        for status in ['invalid', 'resolved', 'declined']:
            response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id),
                                          {'data': {'title': 'complaint title',
                                                    'description': 'complaint description',
                                                    'author': user_data,
                                                    'status': 'claim'
            }})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.json['data']['status'], 'claim')
            complaint = response.json['data']

            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, complaint['id'], self.tender_token),
                {'data': {'status': 'answered', 'resolution': status * 4, 'resolutionType': status}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']['status'], 'answered')
            self.assertEqual(response.json['data']['resolutionType'], status)

        response = self.set_status('active.pre-qualification', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')
        self.assertEqual(response.json['data']['complaints'][-1]['status'], status)


class TenderStage2UASwitch0BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_set_auction_period(self):
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


class TenderStage2UASwitch1BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_bids = test_tender_bids[:1]

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "unsuccessful")


class TenderStage2UASwitchAuctionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_bids = test_tender_bids

    def test_switch_to_auction(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.auction')

    def test_switch_to_complaint(self):
        for status in ['invalid', 'resolved', 'declined']:
            response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id),
                                          {'data': {'title': 'complaint title',
                                                    'description': 'complaint description',
                                                    'author': author,
                                                    'status': 'claim'}})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.json['data']['status'], 'claim')
            complaint = response.json['data']

            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id,
                                                                                           complaint['id'],
                                                                                           self.tender_token),
                                           {'data': {'status': 'answered',
                                                     'resolution': status * 4,
                                                     'resolutionType': status}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']['status'], 'answered')
            self.assertEqual(response.json['data']['resolutionType'], status)

        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.auction')
        self.assertEqual(response.json['data']['complaints'][-1]['status'], status)

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                      {'data': {'bids': response.json['data']['bids']}})
        self.assertEqual(response.json['data']['status'], 'active.qualification')

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award_id),
                                       {'data': {'status': 'unsuccessful'}})

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award_id),
                                       {'data': {'status': 'unsuccessful'}})

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_set_auction_period(self):
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.tendering')
        item = response.json['data']
        self.assertIn('auctionPeriod', item)
        self.assertIn('shouldStartAfter', item['auctionPeriod'])
        self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'],
                                response.json['data']['tenderPeriod']['endDate'])
        self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {'data': {'auctionPeriod': {'startDate': '9999-01-01T00:00:00+00:00'}}})
        item = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(item['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {'data': {'auctionPeriod': {'startDate': None}}})
        item = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('startDate', item['auctionPeriod'])


class TenderStage2UALotSwitch0BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = test_lots

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')
        self.assertEqual(set([i['status'] for i in response.json['data']["lots"]]), set(['unsuccessful']))

    def test_set_auction_period(self):
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {'data': {'lots': [{'auctionPeriod': {'startDate': '9999-01-01T00:00:00+00:00'}}
                                                          for i in self.lots]}
                                        })
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["lots"][0]['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {'data': {'lots': [{'auctionPeriod': {'startDate': None}}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('auctionPeriod', response.json['data']["lots"][0])
        self.assertNotIn('startDate', response.json['data']["lots"][0]['auctionPeriod'])


class TenderStage2UALotSwitch1BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = test_lots
    initial_bids = test_tender_bids[:1]

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')


class TenderStage2UALotSwitchAuctionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = test_lots
    initial_bids = test_tender_bids

    def test_switch_to_auction(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.auction')

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot in response.json['data']['lots']:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')

        self.assertEqual(response.json['data']['status'], 'active.qualification')

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        while any([i['status'] == 'pending' for i in response.json['data']]):
            award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
            self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award_id),
                                {'data': {'status': 'unsuccessful'}})
            response = self.app.get('/tenders/{}/awards'.format(self.tender_id))

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_set_auction_period(self):
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.tendering')
        item = response.json['data']["lots"][0]
        self.assertIn('auctionPeriod', item)
        self.assertIn('shouldStartAfter', item['auctionPeriod'])
        self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'],
                                response.json['data']['tenderPeriod']['endDate'])
        self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {'data': {'lots': [{'auctionPeriod': {'startDate': '9999-01-01T00:00:00+00:00'}}
                                                          for i in self.lots]}})
        item = response.json['data']["lots"][0]
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(item['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {'data': {'lots': [{'auctionPeriod': {'startDate': None}}
                                                          for i in self.lots]}})
        item = response.json['data']['lots'][0]
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('startDate', item['auctionPeriod'])


class TenderStage2UA2LotSwitch0BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = deepcopy(2 * test_lots)

    def test_switch_to_unsuccessful(self):
        self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')
        self.assertEqual(set([i['status'] for i in response.json['data']["lots"]]), set(['unsuccessful']))

    def test_set_auction_period(self):
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


class TenderStage2UA2LotSwitch1BidResourceTest(TenderStage2UALotSwitch1BidResourceTest):
    initial_lots = deepcopy(2 * test_lots)


class TenderStage2UA2LotSwitchAuctionResourceTest(TenderStage2UALotSwitchAuctionResourceTest):
    initial_lots = deepcopy(2 * test_lots)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUSwitchPreQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUAuctionPeriodResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUComplaintSwitchResourceTest))
    # UA
    suite.addTest(unittest.makeSuite(TenderStage2UASwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UASwitch1BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UASwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotSwitch1BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UA2LotSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UA2LotSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UA2LotSwitchAuctionResourceTest))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
