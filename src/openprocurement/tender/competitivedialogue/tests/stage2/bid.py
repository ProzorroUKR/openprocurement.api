import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.utils import set_bid_lotvalues
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_tender_cd_author,
    test_tender_cd_lots,
    test_tender_cd_tenderer,
    test_tender_cdeu_stage2_data,
    test_tender_cdua_stage2_data,
    test_tender_openeu_bids,
)
from openprocurement.tender.competitivedialogue.tests.stage2.bid_blanks import (  # TenderStage2BidResourceTest; TenderStage2BidFeaturesResourceTest; TenderStage2EUBidResourceTest; TenderStage2EUBidFeaturesResourceTest; TenderStage2EUBidDocumentResourceTest; TenderStage2UABidResourceTest; TenderStage2UABidFeaturesResourceTest
    bids_activation_on_tender_documents_ua,
    bids_invalidation_on_tender_change_eu,
    bids_invalidation_on_tender_change_ua,
    create_tender_biddder_invalid_ua,
    create_tender_bidder_document_nopending_eu,
    create_tender_bidder_firm,
    create_tender_bidder_ua,
    delete_tender_bidder_eu,
    deleted_bid_is_not_restorable,
    features_bidder_eu,
    features_bidder_invalid,
    features_bidder_ua,
    ukrainian_author_id,
)
from openprocurement.tender.openeu.tests.bid import (
    Tender2BidResourceTestMixin,
    TenderBidDocumentResourceTestMixin,
    TenderBidResourceTestMixin,
)
from openprocurement.tender.openua.tests.bid import (
    TenderBidDocumentResourceTestMixin as TenderUABidDocumentResourceTestMixin,
)
from openprocurement.tender.openua.tests.bid import (
    TenderBidRequirementResponseEvidenceTestMixin,
    TenderBidRequirementResponseTestMixin,
)
from openprocurement.tender.openua.tests.bid_blanks import (
    bid_Administrator_change as bid_Administrator_change_ua,
)
from openprocurement.tender.openua.tests.bid_blanks import bids_related_product
from openprocurement.tender.openua.tests.bid_blanks import (
    delete_tender_bidder as delete_tender_bidder_ua,
)
from openprocurement.tender.openua.tests.bid_blanks import (
    deleted_bid_do_not_locks_tender_in_state as deleted_bid_do_not_locks_tender_in_state_ua,
)
from openprocurement.tender.openua.tests.bid_blanks import draft1_bid as one_draft_bid
from openprocurement.tender.openua.tests.bid_blanks import draft2_bids as two_draft_bids
from openprocurement.tender.openua.tests.bid_blanks import (
    get_tender_bidder as get_tender_bidder_ua,
)
from openprocurement.tender.openua.tests.bid_blanks import (
    get_tender_tenderers as get_tender_tenderers_ua,
)
from openprocurement.tender.openua.tests.bid_blanks import (
    patch_tender_bidder as patch_tender_bidder_ua,  # TenderStage2UABidResourceTest
)

test_bids_stage2 = deepcopy(test_tender_openeu_bids)
test_bids_stage2[0]["tenderers"][0] = test_tender_cd_tenderer


class CreateBidMixin:
    def setUp(self):
        super().setUp()
        # Create bid
        bid_data = deepcopy(self.test_bids_data[0])
        bid_data["value"] = {"amount": 500}
        bid_data["status"] = "draft"
        set_bid_lotvalues(bid_data, self.initial_lots)
        bid, bid_token = self.create_bid(self.tender_id, bid_data)
        self.bid_id = bid["id"]
        self.bid_token = bid_token


class TenderStage2EUBidResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, TenderBidResourceTestMixin, Tender2BidResourceTestMixin
):
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_cdeu_stage2_data
    test_bids_data = test_bids_stage2
    initial_lots = test_tender_cd_lots
    author_data = test_tender_cd_author

    test_create_tender_bidder_firm = snitch(create_tender_bidder_firm)
    test_delete_tender_bidder = snitch(delete_tender_bidder_eu)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change_eu)
    test_ukrainian_author_id = snitch(ukrainian_author_id)
    # TODO: undone that
    test_create_tender_biddder_invalid = None
    test_bids_related_product = snitch(bids_related_product)

    def setUp(self):
        super().setUp()
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.tender_lots = response.json["data"]["lots"]
        self.test_bids_data = []
        for bid in test_tender_openeu_bids:
            bid_data = deepcopy(bid)
            bid_data["tenderers"][0]["identifier"]["id"] = self.initial_data["shortlistedFirms"][0]["identifier"]["id"]
            set_bid_lotvalues(bid_data, self.tender_lots)
            self.test_bids_data.append(bid_data)


class TenderStage2EUBidFeaturesResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_cdeu_stage2_data
    test_bids_data = test_bids_stage2
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        self.app.authorization = ("Basic", ("broker", ""))

    def create_tender(self, initial_data=None):
        if initial_data:
            super().create_tender(initial_data=initial_data)

    test_features_bidder = snitch(features_bidder_eu)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


@patch(
    "openprocurement.tender.core.procedure.state.bid_document.BID_PROPOSAL_DOC_REQUIRED_FROM",
    get_now() + timedelta(days=1),
)
class TenderStage2EUBidDocumentResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, TenderBidDocumentResourceTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.tendering"
    test_bids_data = test_bids_stage2
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        # Create bid
        test_bid_1 = deepcopy(test_tender_openeu_bids[0])
        test_bid_1["tenderers"] = [test_tender_cd_tenderer]
        set_bid_lotvalues(test_bid_1, self.initial_lots)
        bid, bid_token = self.create_bid(self.tender_id, test_bid_1)
        self.bid_id = bid["id"]
        self.bid_token = bid_token
        # create second bid
        test_bid_2 = deepcopy(test_tender_openeu_bids[1])
        test_bid_2["tenderers"] = [test_tender_cd_tenderer]
        set_bid_lotvalues(test_bid_2, self.initial_lots)
        bid2, bid2_token = self.create_bid(self.tender_id, test_bid_2)
        self.bid2_id = bid2["id"]
        self.bid2_token = bid2_token

    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending_eu)


class TenderStage2UABidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_data = test_tender_cdua_stage2_data
    test_bids_data = test_bids_stage2
    initial_lots = test_tender_cd_lots

    test_create_tender_biddder_invalid = snitch(create_tender_biddder_invalid_ua)
    test_create_tender_bidder = snitch(create_tender_bidder_ua)
    test_patch_tender_bidder = snitch(patch_tender_bidder_ua)
    test_get_tender_bidder = snitch(get_tender_bidder_ua)
    test_delete_tender_bidder = snitch(delete_tender_bidder_ua)
    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_deleted_bid_do_not_locks_tender_in_state = snitch(deleted_bid_do_not_locks_tender_in_state_ua)
    test_get_tender_tenderers = snitch(get_tender_tenderers_ua)
    test_bid_Administrator_change = snitch(bid_Administrator_change_ua)
    test_1_draft_bid = snitch(one_draft_bid)
    test_2_draft_bids = snitch(two_draft_bids)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change_ua)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents_ua)
    test_bids_related_product = snitch(bids_related_product)


class TenderStage2UABidFeaturesResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_data = test_tender_cdua_stage2_data
    test_bids_data = test_bids_stage2
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        self.app.authorization = ("Basic", ("broker", ""))

    def create_tender(self, initial_data=None):
        if initial_data:
            super().create_tender(initial_data=initial_data)

    test_features_bidder_ua = snitch(features_bidder_ua)
    test_features_bidder_invalid_ua = snitch(features_bidder_invalid)


class BaseCDUAStage2BidContentWebTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.tendering"
    test_bids_data = test_bids_stage2
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        # Create bid
        bid_data = deepcopy(self.test_bids_data[0])
        bid_data["value"] = {"amount": 500}
        set_bid_lotvalues(bid_data, self.initial_lots)
        bid, bid_token = self.create_bid(self.tender_id, bid_data)
        self.bid_id = bid["id"]
        self.bid_token = bid_token


class TenderStage2UABidDocumentResourceTest(
    TenderUABidDocumentResourceTestMixin,
    BaseCDUAStage2BidContentWebTest,
):
    pass


class TenderEUBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseCompetitiveDialogEUStage2ContentWebTest,
):
    test_bids_data = test_bids_stage2
    initial_status = "active.tendering"
    initial_lots = test_tender_cd_lots


class TenderUABidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseCDUAStage2BidContentWebTest,
):
    test_bids_data = test_bids_stage2
    initial_status = "active.tendering"
    initial_lots = test_tender_cd_lots


class TenderEUBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseCompetitiveDialogEUStage2ContentWebTest,
):
    test_bids_data = test_bids_stage2
    initial_status = "active.tendering"
    initial_lots = test_tender_cd_lots


class TenderUABidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseCDUAStage2BidContentWebTest,
):
    test_bids_data = test_bids_stage2
    initial_status = "active.tendering"
    initial_lots = test_tender_cd_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUBidDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUBidFeaturesResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUBidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UABidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UABidFeaturesResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEUBidRequirementResponseResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderUABidRequirementResponseResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEUBidRequirementResponseEvidenceResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderUABidRequirementResponseEvidenceResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
