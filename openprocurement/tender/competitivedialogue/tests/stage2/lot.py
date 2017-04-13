# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from uuid import uuid4

from openprocurement.api.tests.base import snitch

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    BaseCompetitiveDialogEUWebTest,
    test_tender_stage2_data_ua,
    test_tender_stage2_data_eu
)
from openprocurement.tender.competitivedialogue.tests.stage2.lot_blanks import (
    # TenderStage2EULotResourceTest
    create_tender_lot_invalid_eu,
    patch_tender_lot_eu,
    patch_tender_currency_eu,
    patch_tender_vat_eu,
    get_tender_lot_eu,
    get_tender_lots_eu,
    delete_tender_lot_eu,
    tender_lot_guarantee_eu,
    tender_lot_guarantee_v2_eu,
    # TenderStage2LotEdgeCasesMixin
    question_blocking,
    claim_blocking,
    next_check_value_with_unanswered_question,
    next_check_value_with_unanswered_claim,
    # TenderStage2EULotFeatureResourceTest
    tender_value_eu,
    tender_features_invalid_eu,
    # TenderStage2EULotBidderResourceTest
    create_tender_bidder_invalid_eu,
    patch_tender_bidder_eu,
    # TenderStage2EULotFeatureBidderResourceTest
    create_tender_with_features_bidder_invalid_eu,
    create_tender_with_features_bidder_eu,
    # TenderStage2EULotProcessTest
    one_lot_0bid_eu,
    one_lot_1bid_eu,
    one_lot_2bid_1unqualified,
    one_lot_2bid_eu,
    two_lot_2bid_1lot_del_eu,
    one_lot_3bid_1del,
    one_lot_3bid_1un_eu,
    two_lot_0bid_eu,
    two_lot_2can_eu,
    two_lot_1can,
    two_lot_2bid_0com_1can,
    two_lot_2bid_2com_2win_eu,
    # TenderStage2UALotResourceTest
    create_tender_lot_invalid_ua,
    create_tender_lot,
    patch_tender_lot_ua,
    patch_tender_currency_ua,
    patch_tender_vat_ua,
    get_tender_lot_ua,
    get_tender_lots_ua,
    delete_tender_lot_ua,
    tender_lot_guarantee_ua,
    tender_lot_guarantee_v2_ua,
    # TenderStage2UALotFeatureResourceTest
    tender_value_ua,
    tender_features_invalid_ua,
    # TenderStage2UALotBidderResourceTest
    create_tender_bidder_invalid_ua,
    patch_tender_bidder_ua,
    # TenderStage2UALotFeatureBidderResourceTest
    create_tender_with_features_bidder_invalid_ua,
    create_tender_with_features_bidder_ua,
    # TenderStage2UALotProcessTest
    one_lot_0bid_ua,
    one_lot_1bid_ua,
    one_lot_1bid_patch_ua,
    one_lot_2bid_ua,
    one_lot_3bid_1un_ua,
    two_lot_0bid_ua,
    two_lot_2can_ua,
    two_lot_1bid_0com_1can_ua,
    two_lot_2bid_1lot_del_ua,
    two_lot_1bid_2com_1win_ua,
    two_lot_1bid_0com_0win_ua,
    two_lot_1bid_1com_1win_ua,
    two_lot_2bid_2com_2win_ua,
)

from openprocurement.tender.openeu.tests.base import (
    test_tender_data,
    test_lots,
    test_bids
)


class TenderStage2EULotResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    initial_lots = [deepcopy(test_lots[0]) for i in range(3)]

    def setUp(self):
        super(BaseCompetitiveDialogEUStage2ContentWebTest, self).setUp()
        self.app.authorization = ('Basic', ('broker', ''))

    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid_eu)

    test_patch_tender_lot = snitch(patch_tender_lot_eu)

    test_patch_tender_currency = snitch(patch_tender_currency_eu)

    test_patch_tender_vat = snitch(patch_tender_vat_eu)

    test_get_tender_lot = snitch(get_tender_lot_eu)

    test_get_tender_lots = snitch(get_tender_lots_eu)

    test_delete_tender_lot = snitch(delete_tender_lot_eu)

    test_tender_lot_guarantee = snitch(tender_lot_guarantee_eu)

    test_tender_lot_guarantee_v2 = snitch(tender_lot_guarantee_v2_eu)


class TenderStage2LotEdgeCasesMixin(object):
    expected_status = None

    test_question_blocking = snitch(question_blocking)

    test_claim_blocking = snitch(claim_blocking)

    test_next_check_value_with_unanswered_question = snitch(next_check_value_with_unanswered_question)

    test_next_check_value_with_unanswered_claim = snitch(next_check_value_with_unanswered_claim)


class TenderStage2EULotEdgeCasesTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderStage2LotEdgeCasesMixin):
    initial_auth = ('Basic', ('broker', ''))
    initial_lots = [deepcopy(test_lots[0]) for i in range(2)]
    expected_status = "active.pre-qualification"

    def setUp(self):
        s2_bids = [deepcopy(bid) for bid in test_bids]
        for bid in s2_bids:
            # bid['tenderers'][0]['identifier']['id'] = '00000{}'.format(n)
            bid['tenderers'][0]['identifier']['id'] = self.initial_data['shortlistedFirms'][0]['identifier']['id']
            bid['tenderers'][0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][0]['identifier']['scheme']
        self.initial_bids = s2_bids
        super(TenderStage2EULotEdgeCasesTest, self).setUp()


class TenderStage2EULotFeatureResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_lots = [deepcopy(test_lots[0]) for i in range(3)]
    initial_auth = ('Basic', ('broker', ''))
    test_tender_data = test_tender_data  # TODO: change attribute identifier

    test_tender_value = snitch(tender_value_eu)

    test_tender_features_invalid = snitch(tender_features_invalid_eu)


class TenderStage2EULotBidderResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_lots = deepcopy(test_lots)
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids  # TODO: change attribute identifier

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid_eu) 

    test_patch_tender_bidder = snitch(patch_tender_bidder_eu)


class TenderStage2EULotFeatureBidderResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = deepcopy(test_lots)
    initial_auth = ('Basic', ('broker', ''))
    initial_features = [
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
            "relatedItem": "3",
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
    test_tender_data = test_tender_data  # TODO: change attribute identifier
    test_bids_data = test_bids  # TODO: change attribute identifier

    def __init__(self, *args, **kwargs):
        self.id_first_lot = uuid4().hex
        self.id_first_item = uuid4().hex
        self.initial_lots[0]['id'] = self.id_first_lot
        self.initial_data = deepcopy(self.initial_data)
        self.initial_data['items'][0]['id'] = self.id_first_item
        self.initial_features[0]['relatedItem'] = self.id_first_lot
        self.initial_features[1]['relatedItem'] = self.id_first_item
        super(TenderStage2EULotFeatureBidderResourceTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(TenderStage2EULotFeatureBidderResourceTest, self).setUp()
        self.app.authorization = ('Basic', ('broker', ''))
        self.lot_id = self.initial_lots[0]['id']
        self.create_tender(initial_lots=self.initial_lots, features=self.initial_features)

    test_create_tender_bidder_invalid = snitch(create_tender_with_features_bidder_invalid_eu)

    test_create_tender_bidder = snitch(create_tender_with_features_bidder_eu)


class TenderStage2EULotProcessTest(BaseCompetitiveDialogEUWebTest):

    initial_data = test_tender_stage2_data_eu
    test_lots_data = test_lots  # TODO: change attribute identifier
    test_bids_data = test_bids  # TODO: change attribute identifier

    def setUp(self):
        super(TenderStage2EULotProcessTest, self).setUp()
        self.app.authorization = ('Basic', ('broker', ''))

    def create_tenderers(self, count=1):
        tenderers = []
        for i in xrange(count):
            tenderer = deepcopy(test_bids[0]["tenderers"])
            tenderer[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][i if i < 3 else 3]['identifier']['id']
            tenderer[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][i if i < 3 else 3]['identifier']['scheme']
            tenderers.append(tenderer)
        return tenderers

    def create_tender(self, initial_lots, features=None):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        data = deepcopy(self.initial_data)
        if initial_lots:
            lots = []
            for i in initial_lots:
                lot = deepcopy(i)
                if 'id' not in lot:
                    lot['id'] = uuid4().hex
                lots.append(lot)
            data['lots'] = self.initial_lots = lots
            for i, item in enumerate(data['items']):
                item['relatedLot'] = lots[i % len(lots)]['id']
            for firm in data['shortlistedFirms']:
                firm['lots'] = [dict(id=lot['id']) for lot in lots]
            self.lots_id = [lot['id'] for lot in lots]
        if features:
            for feature in features:
                if feature['featureOf'] == 'lot':
                    feature['relatedItem'] = data['lots'][0]['id']
                if feature['featureOf'] == 'item':
                    feature['relatedItem'] = data['items'][0]['id']
            data['features'] = self.features = features
        response = self.app.post_json('/tenders', {'data': data})
        tender = response.json['data']
        self.tender = tender
        self.tender_token = response.json['access']['token']
        self.tender_id = tender['id']
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=self.tender_id,
                                                                     token=self.tender_token),
                            {'data': {'status': 'draft.stage2'}})

        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=self.tender_id,
                                                                     token=self.tender_token),
                            {'data': {'status': 'active.tendering'}})
        self.app.authorization = auth

    test_1lot_0bid = snitch(one_lot_0bid_eu)

    test_1lot_1bid = snitch(one_lot_1bid_eu)

    test_1lot_2bid_1unqualified = snitch(one_lot_2bid_1unqualified)

    test_1lot_2bid = snitch(one_lot_2bid_eu)

    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del_eu)

    test_1lot_3bid_1del = snitch(one_lot_3bid_1del)

    test_1lot_3bid_1un = snitch(one_lot_3bid_1un_eu)

    test_2lot_0bid = snitch(two_lot_0bid_eu)

    test_2lot_2can = snitch(two_lot_2can_eu)

    test_2lot_1can = snitch(two_lot_1can)

    test_2lot_2bid_0com_1can = snitch(two_lot_2bid_0com_1can)

    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win_eu)


class TenderStage2UALotResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_lots = [deepcopy(test_lots[0]) for i in range(3)]
    test_lots_data = test_lots  # TODO: change attribute identifier

    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid_ua)

    test_patch_tender_lot = snitch(patch_tender_lot_ua)

    test_patch_tender_currency = snitch(patch_tender_currency_ua)

    test_patch_tender_vat = snitch(patch_tender_vat_ua)

    test_get_tender_lot = snitch(get_tender_lot_ua)

    test_get_tender_lots = snitch(get_tender_lots_ua)

    test_delete_tender_lot = snitch(delete_tender_lot_ua)

    test_tender_lot_guarantee = snitch(tender_lot_guarantee_ua)

    test_tender_lot_guarantee_v2 = snitch(tender_lot_guarantee_v2_ua)

    test_create_tender_lot = snitch(create_tender_lot)


class TenderStage2UALotEdgeCasesTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderStage2LotEdgeCasesMixin):
    initial_data = test_tender_stage2_data_ua
    initial_lots = [deepcopy(test_lots[0]) for i in range(2)]
    expected_status = "active.auction"

    def setUp(self):
        s2_bids = [deepcopy(bid) for bid in test_bids]
        for bid in s2_bids:
            # bid['tenderers'][0]['identifier']['id'] = '00000{}'.format(n)
            bid['tenderers'][0]['identifier']['id'] = self.initial_data['shortlistedFirms'][0]['identifier']['id']
            bid['tenderers'][0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][0]['identifier']['scheme']
        self.initial_bids = s2_bids
        super(TenderStage2UALotEdgeCasesTest, self).setUp()


class TenderStage2UALotFeatureResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = [deepcopy(test_lots[0]) for i in range(2)]
    test_tender_data = test_tender_data  # TODO: change attribute identifier

    test_tender_value = snitch(tender_value_ua)

    test_tender_features_invalid = snitch(tender_features_invalid_ua)


class TenderStage2UALotBidderResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    # initial_status = 'active.tendering'
    initial_lots = deepcopy(test_lots)

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid_ua) 

    test_patch_tender_bidder = snitch(patch_tender_bidder_ua)


class TenderStage2UALotFeatureBidderResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = deepcopy(test_lots)
    initial_features = [
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
            "relatedItem": "3",
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

    def __init__(self, *args, **kwargs):
        self.id_first_lot = uuid4().hex
        self.id_first_item = uuid4().hex
        self.initial_lots[0]['id'] = self.id_first_lot
        self.initial_data = deepcopy(self.initial_data)
        self.initial_data['items'][0]['id'] = self.id_first_item
        self.initial_features[0]['relatedItem'] = self.id_first_lot
        self.initial_features[1]['relatedItem'] = self.id_first_item
        super(TenderStage2UALotFeatureBidderResourceTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(TenderStage2UALotFeatureBidderResourceTest, self).setUp()
        self.app.authorization = ('Basic', ('broker', ''))
        self.lot_id = self.initial_lots[0]['id']
        self.create_tender(initial_lots=self.initial_lots, features=self.initial_features)

    test_create_tender_bidder_invalid = snitch(create_tender_with_features_bidder_invalid_ua)

    test_create_tender_bidder = snitch(create_tender_with_features_bidder_ua)


class TenderStage2UALotProcessTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_data = test_tender_stage2_data_ua
    test_lots_data = test_lots  # TODO: change attribute identifier
    test_bids_data = test_bids  # TODO: change attribute identifier

    def setUp(self):
        super(BaseCompetitiveDialogUAStage2ContentWebTest, self).setUp()
        self.app.authorization = ('Basic', ('broker', ''))

    def create_tenderers(self, count=1):
        tenderers = []
        for i in xrange(count):
            tenderer = deepcopy(test_bids[0]["tenderers"])
            tenderer[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][i if i < 3 else 3]['identifier']['id']
            tenderer[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][i if i < 3 else 3]['identifier']['scheme']
            tenderers.append(tenderer)
        return tenderers

    def create_tender(self, initial_lots, features=None):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        data = deepcopy(self.initial_data)
        if initial_lots:
            lots = []
            for i in initial_lots:
                lot = deepcopy(i)
                if 'id' not in lot:
                    lot['id'] = uuid4().hex
                lots.append(lot)
            data['lots'] = self.initial_lots = lots
            for i, item in enumerate(data['items']):
                item['relatedLot'] = lots[i % len(lots)]['id']
            for firm in data['shortlistedFirms']:
                firm['lots'] = [dict(id=lot['id']) for lot in lots]
            self.lots_id = [lot['id'] for lot in lots]
        if features:
            for feature in features:
                if feature['featureOf'] == 'lot':
                    feature['relatedItem'] = data['lots'][0]['id']
                if feature['featureOf'] == 'item':
                    feature['relatedItem'] = data['items'][0]['id']
            data['features'] = self.features = features
        response = self.app.post_json('/tenders', {'data': data})
        tender = response.json['data']
        self.tender = tender
        self.tender_token = response.json['access']['token']
        self.tender_id = tender['id']
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=self.tender_id,
                                                                     token=self.tender_token),
                            {'data': {'status': 'draft.stage2'}})

        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=self.tender_id,
                                                                     token=self.tender_token),
                            {'data': {'status': 'active.tendering'}})
        self.app.authorization = auth

    test_1lot_0bid = snitch(one_lot_0bid_ua)

    test_1lot_1bid = snitch(one_lot_1bid_ua)

    test_1lot_1bid_patch = snitch(one_lot_1bid_patch_ua)

    test_1lot_2bid = snitch(one_lot_2bid_ua)

    test_1lot_3bid_1un = snitch(one_lot_3bid_1un_ua)

    test_2lot_0bid = snitch(two_lot_0bid_ua)

    test_2lot_2can = snitch(two_lot_2can_ua)

    test_2lot_1bid_0com_1can = snitch(two_lot_1bid_0com_1can_ua)

    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del_ua)

    test_2lot_1bid_2com_1win = snitch(two_lot_1bid_2com_1win_ua)

    test_2lot_1bid_0com_0win = snitch(two_lot_1bid_0com_0win_ua)

    test_2lot_1bid_1com_1win = snitch(two_lot_1bid_1com_1win_ua)

    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win_ua)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EULotResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotProcessTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotFeatureResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotFeatureBidderResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
