import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.lot_blanks import tender_value
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogEUStage2WebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_tender_cd_author,
    test_tender_cdeu_stage2_data,
    test_tender_cdua_stage2_data,
)
from openprocurement.tender.competitivedialogue.tests.stage2.lot_blanks import (
    create_tender_bidder_invalid,
    create_tender_lot,
    create_tender_lot_invalid,
    create_tender_with_features_bidder,
    create_tender_with_features_bidder_invalid,
    delete_tender_lot,
    get_tender_lot,
    get_tender_lots,
    one_lot_0bid,
    one_lot_0bid_ua,
    one_lot_1bid,
    one_lot_1bid_patch_ua,
    one_lot_2bid,
    one_lot_2bid_1un,
    one_lot_2bid_ua,
    one_lot_3bid_1del,
    one_lot_3bid_1un,
    one_lot_3bid_1un_ua,
    patch_tender_bidder,
    patch_tender_bidder_ua,
    patch_tender_currency,
    patch_tender_lot,
    patch_tender_vat,
    tender_lot_guarantee,
    tender_lot_guarantee_v2,
    two_lot_0bid,
    two_lot_0bid_ua,
    two_lot_1bid_0com_0win_ua,
    two_lot_1bid_0com_1can_ua,
    two_lot_1bid_1com_1win_ua,
    two_lot_1bid_2com_1win_ua,
    two_lot_1can,
    two_lot_2bid_0com_1can,
    two_lot_2bid_1lot_del,
    two_lot_2bid_2com_2win,
    two_lot_2bid_2com_2win_ua,
    two_lot_2can,
)
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.openeu.tests.base import (
    test_tender_openeu_bids,
    test_tender_openeu_data,
    test_tender_openeu_lots,
)
from openprocurement.tender.openeu.tests.lot import TenderLotEdgeCasesTestMixin


class TenderStage2EULotResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = [deepcopy(test_tender_openeu_lots[0]) for i in range(3)]

    def setUp(self):
        super(BaseCompetitiveDialogEUStage2ContentWebTest, self).setUp()
        self.app.authorization = ("Basic", ("broker", ""))

    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid)
    test_patch_tender_lot = snitch(patch_tender_lot)
    test_patch_tender_currency = snitch(patch_tender_currency)
    test_patch_tender_vat = snitch(patch_tender_vat)
    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_delete_tender_lot = snitch(delete_tender_lot)
    test_tender_lot_guarantee = snitch(tender_lot_guarantee)
    test_tender_lot_guarantee_v2 = snitch(tender_lot_guarantee_v2)


class TenderStage2EULotEdgeCasesTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderLotEdgeCasesTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = [deepcopy(test_tender_openeu_lots[0]) for i in range(2)]

    def setUp(self):
        identifier = self.initial_data["shortlistedFirms"][0]["identifier"]
        s2_bids = [deepcopy(bid) for bid in test_tender_openeu_bids]
        for bid in s2_bids:
            bid["tenderers"][0]["identifier"]["id"] = identifier["id"]
            bid["tenderers"][0]["identifier"]["scheme"] = identifier["scheme"]
        self.initial_bids = s2_bids
        self.test_author = test_tender_cd_author
        super().setUp()


class TenderStage2EULotFeatureResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = [deepcopy(test_tender_openeu_lots[0]) for i in range(2)]
    initial_auth = ("Basic", ("broker", ""))
    invalid_feature_value = 1
    max_feature_value = 0.99
    sum_of_max_value_of_all_features = 0.99

    test_tender_value = snitch(tender_value)


class TenderStage2EULotBidderResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = deepcopy(test_tender_openeu_lots)
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identifier

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class TenderStage2EULotFeatureBidderResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = deepcopy(test_tender_openeu_lots)
    initial_auth = ("Basic", ("broker", ""))
    initial_features = [
        {
            "code": "code_item",
            "featureOf": "item",
            "relatedItem": "1",
            "title": "item feature",
            "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
        },
        {
            "code": "code_lot",
            "featureOf": "lot",
            "relatedItem": "3",
            "title": "lot feature",
            "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
        },
        {
            "code": "code_tenderer",
            "featureOf": "tenderer",
            "title": "tenderer feature",
            "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
        },
    ]
    test_tender_data = test_tender_openeu_data  # TODO: change attribute identifier
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identifier

    def __init__(self, *args, **kwargs):
        self.id_first_lot = uuid4().hex
        self.id_first_item = uuid4().hex
        self.initial_lots[0]["id"] = self.id_first_lot
        self.initial_data = deepcopy(self.initial_data)
        self.initial_data["items"][0]["id"] = self.id_first_item
        self.initial_features[0]["relatedItem"] = self.id_first_lot
        self.initial_features[1]["relatedItem"] = self.id_first_item
        super().__init__(*args, **kwargs)

    def setUp(self):
        super().setUp()
        self.app.authorization = ("Basic", ("broker", ""))
        self.lot_id = self.initial_lots[0]["id"]
        self.create_tender(initial_lots=self.initial_lots, features=self.initial_features)

    test_create_tender_bidder_invalid = snitch(create_tender_with_features_bidder_invalid)
    test_create_tender_bidder = snitch(create_tender_with_features_bidder)


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM",
    get_now() + timedelta(days=1),
)
class TenderStage2EULotProcessTest(BaseCompetitiveDialogEUStage2WebTest):
    initial_data = test_tender_cdeu_stage2_data
    test_lots_data = test_tender_openeu_lots  # TODO: change attribute identifier
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identifier

    def setUp(self):
        super().setUp()
        self.app.authorization = ("Basic", ("broker", ""))

    def create_tenderers(self, count=1):
        firm = self.initial_data["shortlistedFirms"]
        tenderers = []
        for i in range(count):
            tenderer = deepcopy(test_tender_openeu_bids[0]["tenderers"])
            tenderer[0]["identifier"]["id"] = firm[i if i < 3 else 3]["identifier"]["id"]
            tenderer[0]["identifier"]["scheme"] = firm[i if i < 3 else 3]["identifier"]["scheme"]
            tenderers.append(tenderer)
        return tenderers

    def create_tender(self, initial_lots, features=None):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("competitive_dialogue", ""))
        data = deepcopy(self.initial_data)
        config = deepcopy(self.initial_config)
        if initial_lots:
            lots = []
            for i in initial_lots:
                lot = deepcopy(i)
                if "id" not in lot:
                    lot["id"] = uuid4().hex
                lots.append(lot)
            data["lots"] = self.initial_lots = lots
            for i, item in enumerate(data["items"]):
                item["relatedLot"] = lots[i % len(lots)]["id"]
            for firm in data["shortlistedFirms"]:
                firm["lots"] = [{"id": lot["id"]} for lot in lots]
            self.lots_id = [lot["id"] for lot in lots]
        if features:
            for feature in features:
                if feature["featureOf"] == "lot":
                    feature["relatedItem"] = data["lots"][0]["id"]
                if feature["featureOf"] == "item":
                    feature["relatedItem"] = data["items"][0]["id"]
            data["features"] = self.features = features
        response = self.app.post_json("/tenders", {"data": data, "config": config})
        tender = response.json["data"]
        self.tender = tender
        self.tender_token = response.json["access"]["token"]
        self.tender_id = tender["id"]
        self.app.authorization = ("Basic", ("competitive_dialogue", ""))
        self.app.patch_json(
            "/tenders/{id}?acc_token={token}".format(id=self.tender_id, token=self.tender_token),
            {"data": {"status": "draft.stage2"}},
        )

        add_criteria(self)

        self.app.authorization = ("Basic", ("broker", ""))
        self.app.patch_json(
            "/tenders/{id}?acc_token={token}".format(id=self.tender_id, token=self.tender_token),
            {"data": {"status": "active.tendering"}},
        )
        self.app.authorization = auth

    test_1lot_0bid = snitch(one_lot_0bid)
    test_1lot_1bid = snitch(one_lot_1bid)
    test_1lot_2bid_1unqualified = snitch(one_lot_2bid_1un)
    test_1lot_2bid = snitch(one_lot_2bid)
    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del)
    test_1lot_3bid_1del = snitch(one_lot_3bid_1del)
    test_1lot_3bid_1un = snitch(one_lot_3bid_1un)
    test_2lot_0bid = snitch(two_lot_0bid)
    test_2lot_2can = snitch(two_lot_2can)
    test_2lot_1can = snitch(two_lot_1can)
    test_2lot_2bid_0com_1can = snitch(two_lot_2bid_0com_1can)
    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win)


class TenderStage2UALotResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = [deepcopy(test_tender_openeu_lots[0]) for i in range(3)]
    test_lots_data = test_tender_openeu_lots  # TODO: change attribute identifier

    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid)
    test_create_tender_lot = snitch(create_tender_lot)
    test_patch_tender_lot = snitch(patch_tender_lot)
    test_patch_tender_currency = snitch(patch_tender_currency)
    test_patch_tender_vat = snitch(patch_tender_vat)
    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_delete_tender_lot = snitch(delete_tender_lot)
    test_tender_lot_guarantee = snitch(tender_lot_guarantee)
    test_tender_lot_guarantee_v2 = snitch(tender_lot_guarantee_v2)


class TenderStage2UALotEdgeCasesTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderLotEdgeCasesTestMixin):
    initial_data = test_tender_cdua_stage2_data
    initial_lots = [deepcopy(test_tender_openeu_lots[0]) for i in range(2)]

    def setUp(self):
        identifier = self.initial_data["shortlistedFirms"][0]["identifier"]
        s2_bids = [deepcopy(bid) for bid in test_tender_openeu_bids]
        for bid in s2_bids:
            bid["tenderers"][0]["identifier"]["id"] = identifier["id"]
            bid["tenderers"][0]["identifier"]["scheme"] = identifier["scheme"]
        self.initial_bids = s2_bids
        self.test_author = test_tender_cd_author
        super().setUp()


class TenderStage2UALotFeatureResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = [deepcopy(test_tender_openeu_lots[0]) for i in range(2)]
    invalid_feature_value = 1
    max_feature_value = 0.99
    sum_of_max_value_of_all_features = 0.99

    test_tender_value = snitch(tender_value)


class TenderStage2UALotBidderResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    # initial_status = 'active.tendering'
    initial_lots = deepcopy(test_tender_openeu_lots)
    test_bids_data = test_tender_openeu_bids

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder_ua)


class TenderStage2UALotFeatureBidderResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = deepcopy(test_tender_openeu_lots)
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identifier
    test_tender_data = test_tender_openeu_data  # TODO: change attribute identifier
    initial_features = [
        {
            "code": "code_item",
            "featureOf": "item",
            "relatedItem": "1",
            "title": "item feature",
            "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
        },
        {
            "code": "code_lot",
            "featureOf": "lot",
            "relatedItem": "3",
            "title": "lot feature",
            "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
        },
        {
            "code": "code_tenderer",
            "featureOf": "tenderer",
            "title": "tenderer feature",
            "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
        },
    ]

    def __init__(self, *args, **kwargs):
        self.id_first_lot = uuid4().hex
        self.id_first_item = uuid4().hex
        self.initial_lots[0]["id"] = self.id_first_lot
        self.initial_data = deepcopy(self.initial_data)
        self.initial_data["items"][0]["id"] = self.id_first_item
        self.initial_features[0]["relatedItem"] = self.id_first_lot
        self.initial_features[1]["relatedItem"] = self.id_first_item
        super().__init__(*args, **kwargs)

    def setUp(self):
        super().setUp()
        self.app.authorization = ("Basic", ("broker", ""))
        self.lot_id = self.initial_lots[0]["id"]
        self.create_tender(initial_lots=self.initial_lots, features=self.initial_features)

    test_create_tender_bidder_invalid = snitch(create_tender_with_features_bidder_invalid)
    test_create_tender_bidder = snitch(create_tender_with_features_bidder)


class TenderStage2UALotProcessTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_data = test_tender_cdua_stage2_data
    test_lots_data = test_tender_openeu_lots  # TODO: change attribute identifier
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identifier

    def setUp(self):
        super(BaseCompetitiveDialogUAStage2ContentWebTest, self).setUp()
        self.app.authorization = ("Basic", ("broker", ""))

    def create_tenderers(self, count=1):
        firm = self.initial_data["shortlistedFirms"]
        tenderers = []
        for i in range(count):
            tenderer = deepcopy(test_tender_openeu_bids[0]["tenderers"])
            tenderer[0]["identifier"]["id"] = firm[i if i < 3 else 3]["identifier"]["id"]
            tenderer[0]["identifier"]["scheme"] = firm[i if i < 3 else 3]["identifier"]["scheme"]
            tenderers.append(tenderer)
        return tenderers

    def create_tender(self, initial_lots, features=None):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("competitive_dialogue", ""))
        data = deepcopy(self.initial_data)
        config = deepcopy(self.initial_config)
        if initial_lots:
            lots = []
            for i in initial_lots:
                lot = deepcopy(i)
                if "id" not in lot:
                    lot["id"] = uuid4().hex
                lots.append(lot)
            data["lots"] = self.initial_lots = lots
            for i, item in enumerate(data["items"]):
                item["relatedLot"] = lots[i % len(lots)]["id"]
            for firm in data["shortlistedFirms"]:
                firm["lots"] = [{"id": lot["id"]} for lot in lots]
            for milestone in data["milestones"]:
                milestone["relatedLot"] = lots[0]["id"]
            self.lots_id = [lot["id"] for lot in lots]
        if features:
            for feature in features:
                if feature["featureOf"] == "lot":
                    feature["relatedItem"] = data["lots"][0]["id"]
                if feature["featureOf"] == "item":
                    feature["relatedItem"] = data["items"][0]["id"]
            data["features"] = self.features = features
        response = self.app.post_json("/tenders", {"data": data, "config": config})
        tender = response.json["data"]
        self.tender = tender
        self.tender_token = response.json["access"]["token"]
        self.tender_id = tender["id"]
        self.app.authorization = ("Basic", ("competitive_dialogue", ""))
        self.app.patch_json(
            "/tenders/{id}?acc_token={token}".format(id=self.tender_id, token=self.tender_token),
            {"data": {"status": "draft.stage2"}},
        )

        add_criteria(self)
        self.app.authorization = ("Basic", ("broker", ""))
        self.app.patch_json(
            "/tenders/{id}?acc_token={token}".format(id=self.tender_id, token=self.tender_token),
            {"data": {"status": "active.tendering"}},
        )
        self.app.authorization = auth

    test_1lot_0bid = snitch(one_lot_0bid_ua)
    test_1lot_1bid = snitch(one_lot_1bid)
    test_1lot_1bid_patch = snitch(one_lot_1bid_patch_ua)
    test_1lot_2bid = snitch(one_lot_2bid_ua)
    test_1lot_3bid_1un = snitch(one_lot_3bid_1un_ua)
    test_2lot_0bid = snitch(two_lot_0bid_ua)
    test_2lot_2can = snitch(two_lot_2can)
    test_2lot_1bid_0com_1can = snitch(two_lot_1bid_0com_1can_ua)
    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del)
    test_2lot_1bid_2com_1win = snitch(two_lot_1bid_2com_1win_ua)
    test_2lot_1bid_0com_0win = snitch(two_lot_1bid_0com_0win_ua)
    test_2lot_1bid_1com_1win = snitch(two_lot_1bid_1com_1win_ua)
    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win_ua)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EULotResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EULotBidderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EULotFeatureBidderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EULotProcessTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UALotResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UALotFeatureResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UALotBidderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UALotFeatureBidderResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
