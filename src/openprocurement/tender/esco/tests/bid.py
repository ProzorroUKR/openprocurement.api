import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from esculator import escp, npv

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    bid_proposal_doc,
    create_tender_bid_document_json_bulk,
    create_tender_bid_with_document,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_documents,
    patch_pending_bid,
)
from openprocurement.tender.belowthreshold.tests.utils import set_bid_lotvalues
from openprocurement.tender.esco.procedure.utils import to_decimal
from openprocurement.tender.esco.tests.base import (
    NBU_DISCOUNT_RATE,
    BaseESCOContentWebTest,
    test_tender_esco_bids,
    test_tender_esco_features_data,
    test_tender_esco_lots,
)
from openprocurement.tender.esco.tests.bid_blanks import (
    bid_Administrator_change,
    bids_activation_on_tender_documents,
    bids_invalidation_on_tender_change,
    create_tender_bid,
    create_tender_bid_31_12,
    create_tender_bid_invalid,
    create_tender_bid_invalid_funding_kind_budget,
    create_tender_bid_lot,
    create_tender_bid_no_scale_invalid,
    delete_tender_bidder,
    features_bid,
    features_bid_invalid,
    patch_and_put_document_into_invalid_bid,
    patch_tender_bid,
)
from openprocurement.tender.openeu.tests.bid import CreateBidMixin
from openprocurement.tender.openeu.tests.bid_blanks import (
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
    create_tender_bidder_document,
    create_tender_bidder_document_nopending,
    download_tender_bidder_document,
    get_tender_bidder,
    get_tender_bidder_document,
    get_tender_bidder_document_ds,
    get_tender_tenderers,
    not_found,
    patch_tender_bidder_document,
    patch_tender_bidder_document_private_json,
    put_tender_bidder_document,
    put_tender_bidder_document_private_json,
)
from openprocurement.tender.openua.tests.bid import (
    TenderBidRequirementResponseEvidenceTestMixin,
    TenderBidRequirementResponseTestMixin,
    bids_related_product,
    patch_tender_with_bids_lots_none,
)

bid_amount_performance = round(
    float(
        to_decimal(
            npv(
                test_tender_esco_bids[0]["value"]["contractDuration"]["years"],
                test_tender_esco_bids[0]["value"]["contractDuration"]["days"],
                test_tender_esco_bids[0]["value"]["yearlyPaymentsPercentage"],
                test_tender_esco_bids[0]["value"]["annualCostsReduction"],
                get_now(),
                NBU_DISCOUNT_RATE,
            )
        )
    ),
    2,
)

bid_amount = round(
    float(
        to_decimal(
            escp(
                test_tender_esco_bids[0]["value"]["contractDuration"]["years"],
                test_tender_esco_bids[0]["value"]["contractDuration"]["days"],
                test_tender_esco_bids[0]["value"]["yearlyPaymentsPercentage"],
                test_tender_esco_bids[0]["value"]["annualCostsReduction"],
                get_now(),
            )
        )
    ),
    2,
)


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
    get_now() + timedelta(days=1),
)
class TenderBidResourceTest(BaseESCOContentWebTest):
    initial_status = "active.tendering"
    test_bids_data = test_tender_esco_bids
    initial_lots = test_tender_esco_lots
    author_data = test_tender_below_author
    expected_bid_amount_performance = bid_amount_performance
    expected_bid_amount = bid_amount

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_create_tender_bid = snitch(create_tender_bid)
    test_patch_tender_bid = snitch(patch_tender_bid)
    test_get_tender_bidder = snitch(get_tender_bidder)
    test_get_tender_tenderers = snitch(get_tender_tenderers)

    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)

    test_delete_tender_bidder = snitch(delete_tender_bidder)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change)

    test_create_tender_bid_invalid_funding_kind_budget = snitch(create_tender_bid_invalid_funding_kind_budget)
    test_create_tender_bid_31_12 = snitch(create_tender_bid_31_12)

    test_create_tender_bid_no_scale_invalid = snitch(create_tender_bid_no_scale_invalid)
    test_bid_proposal_doc = snitch(bid_proposal_doc)
    test_patch_pending_bid = snitch(patch_pending_bid)

    test_bids_related_product = snitch(bids_related_product)

    def setUp(self):
        super().setUp()
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.tender_lots = response.json["data"]["lots"]
        self.test_bids_data = []
        for bid in test_tender_esco_bids:
            bid_data = deepcopy(bid)
            set_bid_lotvalues(bid_data, self.tender_lots)
            self.test_bids_data.append(bid_data)


class Tender2LotBidResourceTest(BaseESCOContentWebTest):
    test_bids_data = test_tender_esco_bids
    initial_lots = 2 * test_tender_esco_lots
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)
    test_create_tender_bid = snitch(create_tender_bid_lot)


class TenderBidFeaturesResourceTest(BaseESCOContentWebTest):
    initial_status = "active.tendering"
    initial_data = test_tender_esco_features_data
    test_bids_data = test_tender_esco_bids

    test_features_bid = snitch(features_bid)
    test_features_bid_invalid = snitch(features_bid_invalid)


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
    get_now() + timedelta(days=1),
)
class TenderBidDocumentResourceTest(BaseESCOContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.tendering"
    initial_lots = test_tender_esco_lots
    initial_bids = test_bids_data = test_tender_esco_bids

    def setUp(self):
        super().setUp()
        self.bid_id = self.initial_bids[0]["id"]
        self.bid_token = self.initial_bids_tokens[self.bid_id]
        self.bid2_id = self.initial_bids[1]["id"]
        self.bid2_token = self.initial_bids_tokens[self.bid2_id]

    test_patch_and_put_document_into_invalid_bid = snitch(patch_and_put_document_into_invalid_bid)

    test_create_tender_bid_document_json_bulk = snitch(create_tender_bid_document_json_bulk)
    test_patch_tender_bidder_document_private_json = snitch(patch_tender_bidder_document_private_json)
    test_put_tender_bidder_document_private_json = snitch(put_tender_bidder_document_private_json)
    test_get_tender_bidder_document_ds = snitch(get_tender_bidder_document_ds)

    test_not_found = snitch(not_found)
    test_get_tender_bidder_document = snitch(get_tender_bidder_document)
    test_create_tender_bidder_document = snitch(create_tender_bidder_document)
    test_put_tender_bidder_document = snitch(put_tender_bidder_document)
    test_patch_tender_bidder_document = snitch(patch_tender_bidder_document)
    test_download_tender_bidder_document = snitch(download_tender_bidder_document)

    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending)


class TenderBidBatchDocumentsResourceTest(BaseESCOContentWebTest):
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
        bid_data = deepcopy(test_tender_esco_bids[0])
        bid_data.update({"tenderers": [test_tender_below_organization], "documents": []})

        self.bid_data_wo_docs = bid_data

        super().setUp()


class TenderBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseESCOContentWebTest,
):
    test_bids_data = test_tender_esco_bids
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseESCOContentWebTest,
):
    test_bids_data = test_tender_esco_bids
    initial_status = "active.tendering"


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TenderBidResourceTest)
    suite.addTest(TenderBidFeaturesResourceTest)
    suite.addTest(TenderBidDocumentResourceTest)
    suite.addTest(TenderBidBatchDocumentsResourceTest)
    suite.addTest(TenderBidRequirementResponseResourceTest)
    suite.addTest(TenderBidRequirementResponseEvidenceResourceTest)
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
