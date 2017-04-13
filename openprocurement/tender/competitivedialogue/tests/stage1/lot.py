# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogUAContentWebTest,
    BaseCompetitiveDialogEUContentWebTest,
    test_tender_data_eu,
    test_tender_data_ua,
    test_lots
)
from openprocurement.tender.competitivedialogue.tests.stage1.lot_blanks import (
    # CompetitiveDialogueEULotResourceTest
    create_tender_lot_invalid_eu,
    create_tender_lot_eu,
    patch_tender_lot_eu,
    patch_tender_currency_eu,
    patch_tender_vat_eu,
    get_tender_lot_eu,
    get_tender_lots_eu,
    delete_tender_lot_eu,
    tender_lot_guarantee_eu,
    # CompetitiveDialogueEULotEdgeCasesTest
    question_blocking,
    claim_blocking,
    next_check_value_with_unanswered_question,
    next_check_value_with_unanswered_claim,
    # CompetitiveDialogueEULotFeatureResourceTest
    tender_value_eu,
    tender_features_invalid_eu,
    # CompetitiveDialogueEULotBidderResourceTest
    create_tender_bidder_invalid_eu,
    patch_tender_bidder_eu,
    # CompetitiveDialogueEULotFeatureBidderResourceTest
    create_tender_with_features_bidder_invalid_eu,
    create_tender_with_features_bidder_eu,
    # CompetitiveDialogueEULotProcessTest
    one_lot_0bid_eu,
    one_lot_1bid_eu,
    one_lot_2bid_1unqualified_eu,
    one_lot_2bid_eu,
    two_lot_2bid_1lot_del_eu,
    # one_lot_3bid_1del_eu,
    one_lot_3bid_1un_eu,
    two_lot_0bid_eu,
    two_lot_2can_eu,
    two_lot_1can_eu,
    two_lot_2bid_0com_1can_eu,
    two_lot_2bid_2com_2win_eu,
    # CompetitiveDialogueUALotResourceTest
    create_tender_lot_invalid_ua,
    create_tender_lot_ua,
    patch_tender_lot_ua,
    patch_tender_currency_ua,
    patch_tender_vat_ua,
    get_tender_lot_ua,
    get_tender_lots_ua,
    delete_tender_lot_ua,
    tender_lot_guarantee_ua,
    # CompetitiveDialogueUALotFeatureResourceTest
    tender_value_ua,
    tender_features_invalid_ua,
    # CompetitiveDialogueUALotBidderResourceTest
    create_tender_bidder_invalid_ua,
    patch_tender_bidder_ua,
    # CompetitiveDialogueUALotFeatureBidderResourceTest
    create_tender_with_features_bidder_invalid_ua,
    create_tender_with_features_bidder_ua,
    # CompetitiveDialogueUALotProcessTest
    one_lot_0bid_ua,
    one_lot_1bid_ua,
    one_lot_2bid_1unqualified_ua,
    one_lot_2bid_ua,
    two_lot_2bid_1lot_del_ua,
    one_lot_3bid_1del_ua,
    one_lot_3bid_1un_ua,
    two_lot_0bid_ua,
    two_lot_2can_ua,
    two_lot_1can_ua,
    two_lot_2bid_0com_1can_ua,
    two_lot_2bid_2com_2win_ua,

)

from openprocurement.tender.openeu.tests.base import test_bids

test_bids.append(test_bids[0].copy())  # Minimal number of bits is 3


class CompetitiveDialogueEULotResourceTest(BaseCompetitiveDialogEUContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    test_tender_data = test_tender_data_eu  # TODO: change attribute identifier
    test_lots_data = test_lots  # TODO: change attribute identifier


    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid_eu)

    test_create_tender_lot = snitch(create_tender_lot_eu)

    test_patch_tender_lot = snitch(patch_tender_lot_eu)

    test_patch_tender_currency = snitch(patch_tender_currency_eu)

    test_patch_tender_vat = snitch(patch_tender_vat_eu)

    test_get_tender_lot = snitch(get_tender_lot_eu)

    test_get_tender_lots = snitch(get_tender_lots_eu)

    test_delete_tender_lot = snitch(delete_tender_lot_eu)

    test_tender_lot_guarantee = snitch(tender_lot_guarantee_eu)


class CompetitiveDialogueEULotEdgeCasesTest(BaseCompetitiveDialogEUContentWebTest):
    initial_auth = ('Basic', ('broker', ''))
    initial_lots = test_lots * 2

    def setUp(self):
        uniq_bids = [deepcopy(bid) for bid in test_bids]
        for n, bid in enumerate(uniq_bids):
            bid['tenderers'][0]['identifier']['id'] = '00000{}'.format(n)
        self.initial_bids = uniq_bids
        super(CompetitiveDialogueEULotEdgeCasesTest, self).setUp()

    test_question_blocking  = snitch(question_blocking)

    test_claim_blocking = snitch(claim_blocking)

    test_next_check_value_with_unanswered_question = snitch(next_check_value_with_unanswered_question)

    test_next_check_value_with_unanswered_claim = snitch(next_check_value_with_unanswered_claim)


class CompetitiveDialogueEULotFeatureResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_tender_data = test_tender_data_eu

    test_tender_value = snitch(tender_value_eu)

    test_tender_features_invalid = snitch(tender_features_invalid_eu)


class CompetitiveDialogueEULotBidderResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids  # TODO: change attribute identifier

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid_eu)

    test_patch_tender_bidder = snitch(patch_tender_bidder_eu)


class CompetitiveDialogueEULotFeatureBidderResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids  # TODO: change attribute identifier
    test_tender_data = test_tender_data_eu

    def setUp(self):
        super(CompetitiveDialogueEULotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]['id']
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {
            "items": [
                {
                    'relatedLot': self.lot_id,
                    'id': '1'
                }
            ],
            "features": [
                {
                    "code": "code_item",
                    "featureOf": "item",
                    "relatedItem": "1",
                    "title": u"item feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_lot",
                    "featureOf": "lot",
                    "relatedItem": self.lot_id,
                    "title": u"lot feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_tenderer",
                    "featureOf": "tenderer",
                    "title": u"tenderer feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                }
            ]
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['items'][0]['relatedLot'], self.lot_id)

    test_create_tender_bidder_invalid = snitch(create_tender_with_features_bidder_invalid_eu)

    test_create_tender_bidder = snitch(create_tender_with_features_bidder_eu)


class CompetitiveDialogueEULotProcessTest(BaseCompetitiveDialogEUContentWebTest):
    test_tender_data = test_tender_data_eu  # TODO: change attribute identifier
    test_lots_data = test_lots  # TODO: change attribute identifier
    test_bids_data = test_bids  # TODO: change attribute identifier

    test_1lot_0bid = snitch(one_lot_0bid_eu)

    test_1lot_1bid = snitch(one_lot_1bid_eu)

    test_1lot_2bid_1unqualified = snitch(one_lot_2bid_1unqualified_eu)

    test_1lot_2bid = snitch(one_lot_2bid_eu)

    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del_eu)

    # test_1lot_3bid_1del = snitch(one_lot_3bid_1del_eu)
    def test_1lot_3bid_1del(self):
        test_tender_data = test_tender_data_eu  # TODO: change attribute identifier
        test_lots_data = test_lots  # TODO: change attribute identifier
        test_bids_data = test_bids  # TODO: change attribute identifier
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        self.initial_lots = [response.json['data']]
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bids = []
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        for index, test_bid in enumerate(test_bids):
            bidder_data['identifier']['id'] = str(00037256+index)
            response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                          {'data': {'selfEligible': True,
                                                    'selfQualified': True,
                                                    'tenderers': [bidder_data],
                                                    'lotValues': [{"value": {"amount": 450},
                                                                   'relatedLot': lot_id}]}})
            bids.append({response.json['data']['id']: response.json['access']['token']})

        response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bids[2].keys()[0],
                                                                             bids[2].values()[0]))
        self.assertEqual(response.status, '200 OK')
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               owner_token),
                                      {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.check_chronograph()

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "200 OK")

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "200 OK")

    test_1lot_3bid_1un = snitch(one_lot_3bid_1un_eu)

    test_2lot_0bid = snitch(two_lot_0bid_eu)

    test_2lot_2can = snitch(two_lot_2can_eu)

    test_2lot_1can = snitch(two_lot_1can_eu)

    test_2lot_2bid_0com_1can = snitch(two_lot_2bid_0com_1can_eu)

    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win_eu)


class CompetitiveDialogueUALotResourceTest(BaseCompetitiveDialogUAContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    test_tender_data = test_tender_data_ua  # TODO: change attribute identifier
    test_lots_data = test_lots  # TODO: change attribute identifier

    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid_ua)

    test_create_tender_lot = snitch(create_tender_lot_ua)

    test_patch_tender_lot = snitch(patch_tender_lot_ua)

    test_patch_tender_currency = snitch(patch_tender_currency_ua)

    test_patch_tender_vat = snitch(patch_tender_vat_ua)

    test_get_tender_lot = snitch(get_tender_lot_ua)

    test_get_tender_lots = snitch(get_tender_lots_ua)

    test_delete_tender_lot = snitch(delete_tender_lot_ua)

    test_tender_lot_guarantee = snitch(tender_lot_guarantee_ua)


class CompetitiveDialogueUALotEdgeCasesTest(CompetitiveDialogueEULotEdgeCasesTest):
    initial_data = test_tender_data_ua


class CompetitiveDialogueUALotFeatureResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_tender_data = test_tender_data_ua

    test_tender_value = snitch(tender_value_ua)

    test_tender_features_invalid = snitch(tender_features_invalid_ua)


class CompetitiveDialogueUALotBidderResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids  # TODO: change attribute identifier

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid_ua)

    test_patch_tender_bidder = snitch(patch_tender_bidder_ua)


class CompetitiveDialogueUALotFeatureBidderResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_tender_data = test_tender_data_ua  # TODO: change attribute identifier
    test_bids_data = test_bids  # TODO: change attribute identifier

    def setUp(self):
        super(CompetitiveDialogueUALotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]['id']
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {
            "items": [
                {
                    'relatedLot': self.lot_id,
                    'id': '1'
                }
            ],
            "features": [
                {
                    "code": "code_item",
                    "featureOf": "item",
                    "relatedItem": "1",
                    "title": u"item feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_lot",
                    "featureOf": "lot",
                    "relatedItem": self.lot_id,
                    "title": u"lot feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_tenderer",
                    "featureOf": "tenderer",
                    "title": u"tenderer feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                }
            ]
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['items'][0]['relatedLot'], self.lot_id)

    test_create_tender_bidder_invalid = snitch(create_tender_with_features_bidder_invalid_ua)

    test_create_tender_bidder = snitch(create_tender_with_features_bidder_ua)


class CompetitiveDialogueUALotProcessTest(BaseCompetitiveDialogUAContentWebTest):
    test_tender_data = test_tender_data_ua  # TODO: change attribute identifier
    test_lots_data = test_lots  # TODO: change attribute identifier
    test_bids_data = test_bids  # TODO: change attribute identifier

    test_1lot_0bid = snitch(one_lot_0bid_ua)

    test_1lot_1bid = snitch(one_lot_1bid_ua)

    test_1lot_2bid_1unqualified = snitch(one_lot_2bid_1unqualified_ua)

    test_1lot_2bid = snitch(one_lot_2bid_ua)

    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del_ua)

    # test_1lot_3bid_1del = snitch(one_lot_3bid_1del_ua)
    def test_1lot_3bid_1del(self):
        test_tender_data = test_tender_data_ua  # TODO: change attribute identifier
        # test_lots_data = test_lots  # TODO: change attribute identifier
        # test_bids_data = test_bids  # TODO: change attribute identifier
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        self.initial_lots = [response.json['data']]
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bids = []
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        for index, test_bid in enumerate(test_bids):
            bidder_data['identifier']['id'] = (00037256+index)
            response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                          {'data': {'selfEligible': True,
                                                    'selfQualified': True,
                                                    'tenderers': [bidder_data],
                                                    'lotValues': [{"value": {"amount": 450},
                                                                   'relatedLot': lot_id}]}})
            bids.append({response.json['data']['id']: response.json['access']['token']})

        response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bids[2].keys()[0],
                                                                             bids[2].values()[0]))
        self.assertEqual(response.status, '200 OK')
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               owner_token),
                                      {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.check_chronograph()

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "200 OK")

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "200 OK")

    test_1lot_3bid_1un = snitch(one_lot_3bid_1un_ua)

    test_2lot_0bid = snitch(two_lot_0bid_ua)

    test_2lot_2can = snitch(two_lot_2can_ua)

    test_2lot_1can = snitch(two_lot_1can_ua)

    test_2lot_2bid_0com_1can = snitch(two_lot_2bid_0com_1can_ua)

    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win_ua)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotBidderResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotFeatureResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotProcessTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotFeatureResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotBidderResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotProcessTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotFeatureBidderResourceTest))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
