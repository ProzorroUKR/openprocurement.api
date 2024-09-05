import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.auction import (
    TenderAuctionResourceTestMixin,
    TenderMultipleLotAuctionResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.auction_blanks import (  # TenderStage2EU(UA)SameValueAuctionResourceTest; TenderFeaturesMultilotAuctionResourceTest
    get_tender_lots_auction_features,
    post_tender_auction_not_changed,
    post_tender_auction_reversed,
    post_tender_lots_auction_features,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_tender_cd_lots,
    test_tender_cd_tenderer,
    test_tender_cdeu_features_data,
    test_tender_cdeu_stage2_data,
    test_tender_cdua_stage2_data,
    test_tender_openeu_bids,
)
from openprocurement.tender.competitivedialogue.tests.stage2.auction_blanks import (  # # TenderStage2EU(UA)MultipleLotAuctionResourceTest; TenderStage2EU(UA)FeaturesAuctionResourceTest
    get_tender_auction_feature,
    patch_tender_with_lots_auction,
    post_tender_auction_feature,
)
from openprocurement.tender.openeu.tests.base import test_tender_openeu_lots

test_tender_bids = deepcopy(test_tender_openeu_bids[:2])
for test_bid in test_tender_bids:
    test_bid["tenderers"] = [test_tender_cd_tenderer]


class TenderStage2EUAuctionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderAuctionResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = deepcopy(test_tender_bids)
    initial_lots = test_tender_openeu_lots

    def setUp(self):
        super().setUp()
        # switch to active.pre-qualification
        self.time_shift("active.pre-qualification")
        response = self.check_chronograph()
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")


class TenderStage2EUSameValueAuctionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    # initial_status = 'active.auction'
    tenderer_info = deepcopy(test_tender_cd_tenderer)
    initial_lots = test_tender_openeu_lots

    def setUp(self):
        """Init tender and set status to active.auction"""
        bid_data = deepcopy(test_tender_openeu_bids[0])
        bid_data["tenderers"] = [self.tenderer_info]
        self.initial_bids = [bid_data for i in range(3)]
        super().setUp()
        auth = self.app.authorization
        # switch to active.pre-qualification
        self.set_status("active.pre-qualification", {"status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status("active.auction", {"status": "active.pre-qualification.stand-still"})
        response = self.check_chronograph()
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.auction")
        self.app.authorization = auth

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderStage2EUMultipleLotAuctionResourceTest(
    TenderMultipleLotAuctionResourceTestMixin, TenderStage2EUAuctionResourceTest
):
    initial_lots = deepcopy(2 * test_tender_openeu_lots)

    test_patch_tender_auction = snitch(patch_tender_with_lots_auction)


class TenderStage2EUFeaturesAuctionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_data = test_tender_cdeu_features_data
    features = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": "1",
            "title": "Потужність всмоктування",
            "title_en": "Air Intake",
            "description": "Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.05, "title": "До 1000 Вт"}, {"value": 0.1, "title": "Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": "Відстрочка платежу",
            "title_en": "Postponement of payment",
            "description": "Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": "До 90 днів"}, {"value": 0.1, "title": "Більше 90 днів"}],
        },
    ]
    tenderer_info = deepcopy(test_tender_cd_tenderer)
    initial_status = "active.tendering"
    initial_lots = test_tender_cd_lots

    def setUp(self):
        self.initial_bids = deepcopy(test_tender_openeu_bids[:2])
        self.initial_bids[0].update(
            {
                "parameters": [{"code": i["code"], "value": 0.05} for i in self.features],
                "tenderers": [self.tenderer_info],
            }
        )
        self.initial_bids[1].update(
            {
                "parameters": [{"code": i["code"], "value": 0.1} for i in self.features],
                "tenderers": [self.tenderer_info],
            }
        )
        super().setUp()
        self.prepare_for_auction()

    def create_tender(self):
        data = test_tender_cdeu_stage2_data.copy()
        item = data["items"][0].copy()
        item["id"] = "1"
        data["items"] = [item]
        data["features"] = self.features
        super().create_tender(initial_data=data, initial_bids=self.initial_bids)

    def prepare_for_auction(self):
        """
        Qualify bids and switch to pre-qualification.stand-still (before auction status)
        """
        self.time_shift("active.pre-qualification")
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")

    test_get_tender_auction = snitch(get_tender_auction_feature)
    test_post_tender_auction = snitch(post_tender_auction_feature)


class TenderStage2EUFeaturesMultilotAuctionResourceTest(
    TenderMultipleLotAuctionResourceTestMixin, TenderStage2EUFeaturesAuctionResourceTest
):
    initial_lots = test_tender_openeu_lots * 2
    test_get_tender_auction = snitch(get_tender_lots_auction_features)
    test_post_tender_auction = snitch(post_tender_lots_auction_features)


class TenderStage2UAAuctionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderAuctionResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = deepcopy(test_tender_bids)
    initial_lots = test_tender_cd_lots


class TenderStage2UASameValueAuctionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.auction"
    initial_bids = [
        {
            "tenderers": [test_tender_cd_tenderer],
            "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
            "selfEligible": True,
            "selfQualified": True,
        }
        for i in range(3)
    ]
    initial_lots = test_tender_cd_lots

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)

    def setUp(self):
        bid_data = deepcopy(test_tender_openeu_bids[0])
        bid_data["tenderers"] = [test_tender_cd_tenderer]
        self.initial_bids = [bid_data for i in range(3)]
        super().setUp()


class TenderStage2UAMultipleLotAuctionResourceTest(
    TenderMultipleLotAuctionResourceTestMixin, TenderStage2UAAuctionResourceTest
):
    initial_lots = deepcopy(2 * test_tender_openeu_lots)

    test_patch_tender_auction = snitch(patch_tender_with_lots_auction)


class TenderStage2UAFeaturesAuctionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    features = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": "1",
            "title": "Потужність всмоктування",
            "title_en": "Air Intake",
            "description": "Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.05, "title": "До 1000 Вт"}, {"value": 0.1, "title": "Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": "Відстрочка платежу",
            "title_en": "Postponement of payment",
            "description": "Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": "До 90 днів"}, {"value": 0.1, "title": "Більше 90 днів"}],
        },
    ]
    tenderer_info = deepcopy(test_tender_cd_tenderer)
    initial_status = "active.tendering"
    initial_lots = test_tender_cd_lots

    def setUp(self):
        self.initial_bids = deepcopy(test_tender_openeu_bids[:2])
        self.initial_bids[0].update(
            {
                "parameters": [{"code": i["code"], "value": 0.05} for i in self.features],
                "tenderers": [self.tenderer_info],
            }
        )
        self.initial_bids[1].update(
            {
                "parameters": [{"code": i["code"], "value": 0.1} for i in self.features],
                "tenderers": [self.tenderer_info],
            }
        )
        super().setUp()
        self.app.authorization = ("Basic", ("broker", ""))
        data = test_tender_cdua_stage2_data.copy()
        item = data["items"][0].copy()
        item["id"] = "1"
        item["relatedLot"] = self.initial_lots[0]["id"]
        data["items"] = [item]
        data["features"] = self.features
        self.create_tender(initial_data=data, initial_bids=self.initial_bids, initial_lots=self.initial_lots)

    def create_tender(self, initial_data=None, initial_bids=None, initial_lots=None):
        if initial_data:
            super().create_tender(initial_data=initial_data, initial_bids=initial_bids, initial_lots=initial_lots)

    test_get_tender_auction = snitch(get_tender_auction_feature)
    test_post_tender_auction = snitch(post_tender_auction_feature)


class TenderStage2UAFeaturesMultilotAuctionResourceTest(
    TenderMultipleLotAuctionResourceTestMixin, TenderStage2UAFeaturesAuctionResourceTest
):
    initial_lots = test_tender_openeu_lots * 2
    test_get_tender_auction = snitch(get_tender_lots_auction_features)
    test_post_tender_auction = snitch(post_tender_lots_auction_features)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUSameValueAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUFeaturesAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUFeaturesMultilotAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UAAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UASameValueAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UAFeaturesAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UAFeaturesMultilotAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
