import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.constants_env import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import calculate_date, get_now
from openprocurement.tender.arma.tests.complex_asset.bid_blanks import (
    bid_Administrator_change,
    bids_activation_on_tender_documents,
    create_tender_bid_no_scale_invalid,
    create_tender_bid_with_all_documents,
    create_tender_bid_with_document,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_documents,
    create_tender_bid_with_eligibility_document,
    create_tender_bid_with_eligibility_document_invalid,
    create_tender_bid_with_eligibility_documents,
    create_tender_bid_with_financial_document,
    create_tender_bid_with_financial_document_invalid,
    create_tender_bid_with_financial_documents,
    create_tender_bid_with_qualification_document,
    create_tender_bid_with_qualification_document_invalid,
    create_tender_bid_with_qualification_documents,
    create_tender_biddder_invalid,
    create_tender_bidder,
    not_found,
    patch_and_put_document_into_invalid_bid,
    patch_tender_bidder,
    patch_tender_bidder_document_private_json,
    patch_tender_draft_bidder,
    patch_tender_lot_values_any_order,
)
from openprocurement.tender.arma.tests.simple_asset.base import (
    BaseTenderSimpleAssetContentWebTest,
    test_tender_arma_simple_bids,
    test_tender_arma_simple_criteria,
    test_tender_arma_simple_lots,
)
from openprocurement.tender.core.tests.utils import set_bid_items, set_bid_lotvalues
from openprocurement.tender.open.tests.above_threshold_ua.bid import (
    TenderBidRequirementResponseEvidenceTestMixin,
    TenderBidRequirementResponseTestMixin,
)
from openprocurement.tender.open.tests.above_threshold_ua.bid_blanks import (
    bids_related_product,
    patch_tender_with_bids_lots_none,
)
from openprocurement.tender.open.tests.below_threshold.base import (
    test_tender_below_author,
    test_tender_below_supplier,
)
from openprocurement.tender.open.tests.below_threshold.bid_blanks import (
    bid_proposal_doc,
    create_tender_bid_document_json_bulk,
    patch_pending_bid,
)


class CreateBidMixin:
    base_bid_status = "draft"

    def setUp(self):
        super().setUp()
        self.app.authorization = ("Basic", ("broker", ""))
        bid_data = self.test_bids_data[0].copy()
        bid_data["status"] = self.base_bid_status
        set_bid_items(self, bid_data)
        bid, self.bid_token = self.create_bid(self.tender_id, bid_data)
        self.bid_id = bid["id"]


class TenderBidResourceTest(BaseTenderSimpleAssetContentWebTest):
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_tender_arma_simple_lots
    test_bids_data = test_tender_arma_simple_bids
    author_data = test_tender_below_author

    test_create_tender_bidder = snitch(create_tender_bidder)
    test_create_tender_biddder_invalid = snitch(create_tender_biddder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)
    test_patch_tender_draft_bidder = snitch(patch_tender_draft_bidder)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_create_tender_bid_no_scale_invalid = snitch(create_tender_bid_no_scale_invalid)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)
    test_bids_related_product = snitch(bids_related_product)
    test_bid_proposal_doc = snitch(bid_proposal_doc)
    test_patch_pending_bid = snitch(patch_pending_bid)

    def setUp(self):
        super().setUp()
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.tender_lots = response.json["data"]["lots"]
        self.test_bids_data = []
        for bid in test_tender_arma_simple_bids:
            bid_data = deepcopy(bid)
            set_bid_lotvalues(bid_data, self.tender_lots)
            set_bid_items(self, bid_data)
            self.test_bids_data.append(bid_data)


class Tender2LotBidResourceTest(BaseTenderSimpleAssetContentWebTest):
    test_bids_data = test_tender_arma_simple_bids
    initial_lots = 3 * test_tender_arma_simple_lots
    initial_status = "active.tendering"
    initial_criteria = test_tender_arma_simple_criteria

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)
    test_patch_tender_lot_values_any_order = snitch(patch_tender_lot_values_any_order)


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM",
    calculate_date(get_now(), timedelta(days=1)),
)
class TenderBidDocumentResourceTest(BaseTenderSimpleAssetContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.tendering"
    initial_lots = test_tender_arma_simple_lots
    initial_bids = test_bids_data = test_tender_arma_simple_bids

    def setUp(self):
        super().setUp()
        self.bid_id = self.initial_bids[0]["id"]
        self.bid_token = self.initial_bids_tokens[self.bid_id]
        self.bid2_id = self.initial_bids[1]["id"]
        self.bid2_token = self.initial_bids_tokens[self.bid2_id]

    test_not_found = snitch(not_found)
    test_patch_and_put_document_into_invalid_bid = snitch(patch_and_put_document_into_invalid_bid)
    test_patch_tender_bidder_document_private_json = snitch(patch_tender_bidder_document_private_json)
    test_create_tender_bid_document_json_bulk = snitch(create_tender_bid_document_json_bulk)


class TenderBidBatchDocumentsResourceTest(BaseTenderSimpleAssetContentWebTest):
    initial_lots = test_tender_arma_simple_lots
    initial_status = "active.tendering"

    test_create_tender_bid_with_document_invalid = snitch(create_tender_bid_with_document_invalid)
    test_create_tender_bid_with_document = snitch(create_tender_bid_with_document)
    test_create_tender_bid_with_documents = snitch(create_tender_bid_with_documents)

    test_create_tender_bid_with_eligibility_document_invalid = snitch(
        create_tender_bid_with_eligibility_document_invalid
    )
    test_create_tender_bid_with_eligibility_document = snitch(create_tender_bid_with_eligibility_document)
    test_create_tender_bid_with_eligibility_documents = snitch(create_tender_bid_with_eligibility_documents)

    test_create_tender_bid_with_qualification_document_invalid = snitch(
        create_tender_bid_with_qualification_document_invalid
    )
    test_create_tender_bid_with_qualification_document = snitch(create_tender_bid_with_qualification_document)
    test_create_tender_bid_with_qualification_documents = snitch(create_tender_bid_with_qualification_documents)

    test_create_tender_bid_with_financial_document_invalid = snitch(create_tender_bid_with_financial_document_invalid)
    test_create_tender_bid_with_financial_document = snitch(create_tender_bid_with_financial_document)
    test_create_tender_bid_with_financial_documents = snitch(create_tender_bid_with_financial_documents)

    test_create_tender_bid_with_all_documents = snitch(create_tender_bid_with_all_documents)

    def setUp(self):
        self.bid_data_wo_docs = {
            "tenderers": [test_tender_below_supplier],
            "value": {"amountPercentage": 50},
            "documents": [],
        }
        if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
            self.bid_data_wo_docs["selfEligible"] = True

        super().setUp()


class TenderBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseTenderSimpleAssetContentWebTest,
):
    test_bids_data = test_tender_arma_simple_bids
    initial_status = "active.tendering"
    initial_lots = test_tender_arma_simple_lots


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseTenderSimpleAssetContentWebTest,
):
    test_bids_data = test_tender_arma_simple_bids
    initial_lots = test_tender_arma_simple_lots
    initial_status = "active.tendering"
    tender_auth = ("Basic", ("broker", ""))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotBidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidBatchDocumentsResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidRequirementResponseResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidRequirementResponseEvidenceResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
