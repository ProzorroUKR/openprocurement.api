from unittest.mock import patch
from datetime import timedelta
import unittest
from copy import deepcopy

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch

from openprocurement.tender.openeu.tests.bid import CreateBidMixin
from openprocurement.tender.openeu.tests.bid_blanks import bids_activation_on_tender_documents
from openprocurement.tender.openua.tests.bid import (
    TenderBidDocumentWithDSResourceTestMixin,
    TenderBidRequirementResponseTestMixin,
    TenderBidRequirementResponseEvidenceTestMixin,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogUAContentWebTest,
    BaseCompetitiveDialogEUContentWebTest,
    test_tender_cd_stage1_bids,
    test_tender_cd_tenderer,
    test_tender_cd_lots,
    test_tender_cdeu_features_data,
)
from openprocurement.tender.competitivedialogue.tests.stage1.bid_blanks import (
    patch_tender_with_bids_lots_none,
    create_tender_bidder,
    deleted_bid_is_not_restorable,
    create_tender_bidder_invalid,
    status_jumping,
    create_bid_without_parameters,
    patch_tender_bidder,
    get_tender_bidder,
    deleted_bid_do_not_locks_tender_in_state,
    get_tender_tenderers,
    bids_invalidation_on_tender_change,
    features_bidder,
    features_bidder_invalid,
    get_tender_bidder_document,
    create_tender_bidder_document,
    patch_and_put_document_into_invalid_bid,
    download_tender_bidder_document,
    create_tender_bidder_document_nopending,
    create_tender_bidder_document_description,
    create_tender_bidder_invalid_document_description,
    create_tender_bidder_invalid_confidential_document,
    bids_view_j1446,
)


@patch("openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
       get_now() + timedelta(days=1))
class CompetitiveDialogEUBidResourceTest(BaseCompetitiveDialogEUContentWebTest):

    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_cd_stage1_bids
    docservice = True

    # overwriting TenderBidResourceTestMixin.test_create_tender_bidder
    test_create_tender_bidder = snitch(create_tender_bidder)
    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_status_jumping = snitch(status_jumping)
    test_create_bid_without_parameters = snitch(create_bid_without_parameters)
    test_patch_tender_bidder = snitch(patch_tender_bidder)
    test_get_tender_bidder = snitch(get_tender_bidder)
    test_deleted_bid_do_not_locks_tender_in_state = snitch(deleted_bid_do_not_locks_tender_in_state)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change)


class CompetitiveDialogEU2LotBidResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = 2 * test_tender_cd_lots
    test_bids_data = test_tender_cd_stage1_bids
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)


class CompetitiveDialogEUBidFeaturesResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_data = test_tender_cdeu_features_data
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_cd_stage1_bids

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


@patch("openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
       get_now() + timedelta(days=1))
class CompetitiveDialogEUBidDocumentResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.tendering"
    test_bids_data = test_tender_cd_stage1_bids
    docservice = True

    def setUp(self):
        super(CompetitiveDialogEUBidDocumentResourceTest, self).setUp()
        # Create bid
        bidder_data = deepcopy(test_tender_cd_stage1_bids[0])
        bidder_data["tenderers"][0]["identifier"]["id"] = "00037256"
        bid, bid_token = self.create_bid(self.tender_id, bidder_data)
        self.bid_id = bid["id"]
        self.bid_token = bid_token
        # create second bid
        bidder_data = deepcopy(test_tender_cd_stage1_bids[1])
        bidder_data["tenderers"][0]["identifier"]["id"] = "00037257"
        bid2, bid2_token = self.create_bid(self.tender_id, bidder_data)
        self.bid2_id = bid2["id"]
        self.bid2_token = bid2_token
        bidder_data = deepcopy(test_tender_cd_stage1_bids[1])
        bidder_data["tenderers"][0]["identifier"]["id"] = "00037258"
        bid3, bid3_token = self.create_bid(self.tender_id, bidder_data)
        self.bid3_id = bid3["id"]
        self.bid3_token = bid3_token

    test_get_tender_bidder_document = snitch(get_tender_bidder_document)
    test_create_tender_bidder_document = snitch(create_tender_bidder_document)
    test_patch_and_put_document_into_invalid_bid = snitch(patch_and_put_document_into_invalid_bid)
    test_download_tender_bidder_document = snitch(download_tender_bidder_document)
    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending)
    test_create_tender_bidder_document_description = snitch(create_tender_bidder_document_description)
    test_create_tender_bidder_invalid_document_description = snitch(create_tender_bidder_invalid_document_description)
    test_create_tender_bidder_invalid_confidential_document = snitch(create_tender_bidder_invalid_confidential_document)
    test_bids_view_j1446 = snitch(bids_view_j1446)


class TenderUABidDocumentWithDSWebTest(TenderBidDocumentWithDSResourceTestMixin, BaseCompetitiveDialogUAContentWebTest):
    initial_status = "active.tendering"
    test_bids_data = test_tender_cd_stage1_bids

    def setUp(self):
        super(TenderUABidDocumentWithDSWebTest, self).setUp()
        # Create bid
        bid_data = deepcopy(self.test_bids_data[0])
        bid_data["tenderers"] = [test_tender_cd_tenderer]

        bid, bid_token = self.create_bid(self.tender_id, bid_data)
        self.bid_id = bid["id"]
        self.bid_token = bid_token


class TenderEUBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseCompetitiveDialogEUContentWebTest,
):
    test_bids_data = test_tender_cd_stage1_bids
    initial_status = "active.tendering"


class TenderUABidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseCompetitiveDialogUAContentWebTest,
):
    test_bids_data = test_tender_cd_stage1_bids
    initial_status = "active.tendering"


class TenderEUBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseCompetitiveDialogEUContentWebTest,
):
    test_bids_data = test_tender_cd_stage1_bids
    initial_status = "active.tendering"


class TenderUABidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseCompetitiveDialogUAContentWebTest,
):
    test_bids_data = test_tender_cd_stage1_bids
    initial_status = "active.tendering"


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUBidResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderEUBidRequirementResponseResourceTest))
    suite.addTest(unittest.makeSuite(TenderUABidRequirementResponseResourceTest))
    suite.addTest(unittest.makeSuite(TenderEUBidRequirementResponseEvidenceResourceTest))
    suite.addTest(unittest.makeSuite(TenderUABidRequirementResponseEvidenceResourceTest))

    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
