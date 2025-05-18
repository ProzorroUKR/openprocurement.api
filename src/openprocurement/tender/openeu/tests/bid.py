import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.constants_env import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_supplier,
)
from openprocurement.tender.belowthreshold.tests.bid_blanks import (  # Tender2LotBidResourceTest
    bid_proposal_doc,
    create_tender_bid_document_json_bulk,
    create_tender_bid_with_document,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_documents,
    patch_pending_bid,
    patch_tender_bid_with_exceeded_lot_values,
    patch_tender_lot_values_any_order,
    post_tender_bid_with_exceeded_lot_values,
)
from openprocurement.tender.core.tests.utils import set_bid_items, set_bid_lotvalues
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_tender_openeu_bids,
    test_tender_openeu_criteria,
    test_tender_openeu_features_data,
    test_tender_openeu_lots,
)
from openprocurement.tender.openeu.tests.bid_blanks import (
    bid_Administrator_change,
    bids_activation_on_tender_documents,
    bids_invalidation_on_tender_change,
    create_tender_bid_no_scale_invalid,
    create_tender_bid_with_all_documents,
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
    create_tender_bidder_document,
    create_tender_bidder_document_nopending,
    delete_tender_bidder,
    download_tender_bidder_document,
    features_bidder,
    features_bidder_invalid,
    get_tender_bidder,
    get_tender_bidder_document,
    get_tender_bidder_document_ds,
    get_tender_tenderers,
    not_found,
    patch_and_put_document_into_invalid_bid,
    patch_tender_bidder,
    patch_tender_bidder_document,
    patch_tender_bidder_document_private_json,
    patch_tender_draft_bidder,
    put_tender_bidder_document,
    put_tender_bidder_document_private_json,
)
from openprocurement.tender.openua.tests.bid import (
    TenderBidRequirementResponseEvidenceTestMixin,
    TenderBidRequirementResponseTestMixin,
)
from openprocurement.tender.openua.tests.bid_blanks import (
    bids_related_product,
    patch_tender_with_bids_lots_none,
)


class CreateBidMixin:
    base_bid_status = "draft"

    def setUp(self):
        super().setUp()
        # Create bid
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker', ''))
        bid_data = self.test_bids_data[0].copy()
        bid_data["status"] = self.base_bid_status
        set_bid_items(self, bid_data)
        bid, self.bid_token = self.create_bid(self.tender_id, bid_data)
        self.bid_id = bid["id"]


class TenderBidResourceTestMixin:
    test_create_tender_bidder = snitch(create_tender_bidder)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)


class Tender2BidResourceTestMixin:
    test_create_tender_biddder_invalid = snitch(create_tender_biddder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)
    test_patch_tender_draft_bidder = snitch(patch_tender_draft_bidder)
    test_get_tender_bidder = snitch(get_tender_bidder)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_create_tender_bid_no_scale_invalid = snitch(create_tender_bid_no_scale_invalid)


class TenderBidResourceTest(BaseTenderContentWebTest, TenderBidResourceTestMixin, Tender2BidResourceTestMixin):
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_tender_openeu_lots
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identifier
    author_data = test_tender_below_author

    test_delete_tender_bidder = snitch(delete_tender_bidder)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change)
    test_bids_related_product = snitch(bids_related_product)
    test_bid_proposal_doc = snitch(bid_proposal_doc)
    test_patch_pending_bid = snitch(patch_pending_bid)

    def setUp(self):
        super().setUp()
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.tender_lots = response.json["data"]["lots"]
        self.test_bids_data = []
        for bid in test_tender_openeu_bids:
            bid_data = deepcopy(bid)
            set_bid_lotvalues(bid_data, self.tender_lots)
            set_bid_items(self, bid_data)
            self.test_bids_data.append(bid_data)


class Tender2LotBidResourceTest(BaseTenderContentWebTest):
    test_bids_data = test_tender_openeu_bids
    initial_lots = 3 * test_tender_openeu_lots
    initial_status = "active.tendering"
    initial_criteria = test_tender_openeu_criteria

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)
    test_patch_tender_lot_values_any_order = snitch(patch_tender_lot_values_any_order)
    test_post_tender_bid_with_exceeded_lot_values = snitch(post_tender_bid_with_exceeded_lot_values)
    test_patch_tender_bid_with_exceeded_lot_values = snitch(patch_tender_bid_with_exceeded_lot_values)


class TenderBidFeaturesResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_openeu_features_data
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identificator

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderBidDocumentResourceTestMixin:
    test_not_found = snitch(not_found)
    test_get_tender_bidder_document = snitch(get_tender_bidder_document)
    test_create_tender_bidder_document = snitch(create_tender_bidder_document)
    test_put_tender_bidder_document = snitch(put_tender_bidder_document)
    test_patch_tender_bidder_document = snitch(patch_tender_bidder_document)
    test_download_tender_bidder_document = snitch(download_tender_bidder_document)
    test_patch_tender_bidder_document_private_json = snitch(patch_tender_bidder_document_private_json)


class TenderBidDocumentResourceTest(TenderBidDocumentResourceTestMixin, BaseTenderContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.tendering"
    initial_lots = test_tender_openeu_lots
    initial_bids = test_bids_data = test_tender_openeu_bids  # TODO: change attribute identificator

    def setUp(self):
        super().setUp()
        # Create bid
        self.bid_id = self.initial_bids[0]["id"]
        self.bid_token = self.initial_bids_tokens[self.bid_id]
        self.bid2_id = self.initial_bids[1]["id"]
        self.bid2_token = self.initial_bids_tokens[self.bid2_id]

    test_patch_and_put_document_into_invalid_bid = snitch(patch_and_put_document_into_invalid_bid)
    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending)

    test_create_tender_bid_document_json_bulk = snitch(create_tender_bid_document_json_bulk)
    test_put_tender_bidder_document_private_json = snitch(put_tender_bidder_document_private_json)
    test_get_tender_bidder_document_ds = snitch(get_tender_bidder_document_ds)


class TenderBidBatchDocumentsResourceTest(BaseTenderContentWebTest):
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
            "value": {"amount": 500},
            "selfQualified": True,
            "documents": [],
        }
        if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
            self.bid_data_wo_docs["selfEligible"] = True

        super().setUp()


class TenderBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseTenderContentWebTest,
):
    test_bids_data = test_tender_openeu_bids
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseTenderContentWebTest,
):
    test_bids_data = test_tender_openeu_bids
    initial_status = "active.tendering"
    tender_auth = ("Basic", ("token", ""))
    guarantee_criterion = True


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidBatchDocumentsResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidRequirementResponseResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidRequirementResponseEvidenceResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
