# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from esculator import npv, escp
from openprocurement.api.utils import get_now
from openprocurement.tender.esco.tests.base import (
    BaseESCOContentWebTest,
    NBU_DISCOUNT_RATE,
    test_features_tender_data,
    test_bids,
    test_lots,
)
from openprocurement.tender.belowthreshold.tests.base import test_organization, test_author
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderBidBatchDocumentWithDSResourceTest
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
    # Tender2LotBidResourceTest
    patch_tender_with_bids_lots_none,
    create_tender_bid_contract_data_document_json,
)
from openprocurement.tender.openeu.tests.bid import (
    TenderBidDocumentResourceTestMixin,
    CreateBidMixin,
)
from openprocurement.tender.openua.tests.bid import (
    TenderBidRequirementResponseTestMixin,
    TenderBidRequirementResponseEvidenceTestMixin,
)
from openprocurement.tender.openeu.tests.bid_blanks import (
    # TenderBidDocumentWithDSResourceTest
    patch_tender_bidder_document_private_json,
    put_tender_bidder_document_private_json,
    get_tender_bidder_document_ds,
    # TenderBidDocumentResourceTest
    create_tender_bidder_document_nopending,
    # TenderBidBatchDocumentWithDSResourceTest
    create_tender_bid_with_all_documents,
    create_tender_bid_with_eligibility_document_invalid,
    create_tender_bid_with_financial_document_invalid,
    create_tender_bid_with_qualification_document_invalid,
    create_tender_bid_with_eligibility_document,
    create_tender_bid_with_qualification_document,
    create_tender_bid_with_financial_document,
    create_tender_bid_with_financial_documents,
    create_tender_bid_with_eligibility_documents,
    create_tender_bid_with_qualification_documents,
    get_tender_bidder,
    get_tender_tenderers,
)
from openprocurement.tender.esco.tests.bid_blanks import (
    create_tender_bid_invalid,
    create_tender_bid,
    patch_tender_bid,
    deleted_bid_is_not_restorable,
    bid_Administrator_change,
    bids_activation_on_tender_documents,
    features_bid_invalid,
    features_bid,
    patch_and_put_document_into_invalid_bid,
    # TenderBidResourceTest
    delete_tender_bidder,
    bids_invalidation_on_tender_change,
    deleted_bid_do_not_locks_tender_in_state,
    create_tender_bid_invalid_funding_kind_budget,
    create_tender_bid_31_12,
    create_tender_bid_no_scale_invalid,
    create_tender_bid_with_scale_not_required,
    create_tender_bid_no_scale,
)
from openprocurement.tender.esco.utils import to_decimal


bid_amountPerformance = round(
    to_decimal(
        npv(
            test_bids[0]["value"]["contractDuration"]["years"],
            test_bids[0]["value"]["contractDuration"]["days"],
            test_bids[0]["value"]["yearlyPaymentsPercentage"],
            test_bids[0]["value"]["annualCostsReduction"],
            get_now(),
            NBU_DISCOUNT_RATE,
        )
    ),
    2,
)

bid_amount = round(
    to_decimal(
        escp(
            test_bids[0]["value"]["contractDuration"]["years"],
            test_bids[0]["value"]["contractDuration"]["days"],
            test_bids[0]["value"]["yearlyPaymentsPercentage"],
            test_bids[0]["value"]["annualCostsReduction"],
            get_now(),
        )
    ),
    2,
)


class TenderBidResourceTest(BaseESCOContentWebTest):
    initial_status = "active.tendering"
    test_bids_data = test_bids
    author_data = test_author
    expected_bid_amountPerformance = bid_amountPerformance
    expected_bid_amount = bid_amount

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_create_tender_bid = snitch(create_tender_bid)
    test_patch_tender_bid = snitch(patch_tender_bid)
    test_get_tender_bidder = snitch(get_tender_bidder)
    test_deleted_bid_do_not_locks_tender_in_state = snitch(deleted_bid_do_not_locks_tender_in_state)
    test_get_tender_tenderers = snitch(get_tender_tenderers)

    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)

    test_delete_tender_bidder = snitch(delete_tender_bidder)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change)

    test_create_tender_bid_invalid_funding_kind_budget = snitch(create_tender_bid_invalid_funding_kind_budget)
    test_create_tender_bid_31_12 = snitch(create_tender_bid_31_12)

    test_create_tender_bid_no_scale_invalid = snitch(create_tender_bid_no_scale_invalid)
    test_create_tender_bid_with_scale_not_required = snitch(create_tender_bid_with_scale_not_required)
    test_create_tender_bid_no_scale = snitch(create_tender_bid_no_scale)


class Tender2LotBidResourceTest(BaseESCOContentWebTest):
    test_bids_data = test_bids
    initial_lots = 2 * test_lots
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)


class TenderBidFeaturesResourceTest(BaseESCOContentWebTest):
    initial_status = "active.tendering"
    initial_data = test_features_tender_data
    test_bids_data = test_bids

    test_features_bid = snitch(features_bid)
    test_features_bid_invalid = snitch(features_bid_invalid)


class TenderBidDocumentResourceTest(BaseESCOContentWebTest, TenderBidDocumentResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.tendering"
    test_bids_data = test_bids

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": test_bids[0]})
        bid = response.json["data"]
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]
        # create second bid
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": test_bids[1]})
        bid2 = response.json["data"]
        self.bid2_id = bid2["id"]
        self.bid2_token = response.json["access"]["token"]

    test_patch_and_put_document_into_invalid_bid = snitch(patch_and_put_document_into_invalid_bid)
    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_patch_tender_bidder_document_private_json = snitch(patch_tender_bidder_document_private_json)
    test_put_tender_bidder_document_private_json = snitch(put_tender_bidder_document_private_json)
    test_get_tender_bidder_document_ds = snitch(get_tender_bidder_document_ds)
    test_create_tender_bid_contract_data_document_json = snitch(create_tender_bid_contract_data_document_json)


class TenderBidDocumentWithoutDSResourceTest(TenderBidDocumentResourceTest):
    docservice = False


class TenderBidBatchDocumentsWithDSResourceTest(BaseESCOContentWebTest):
    docservice = True
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
        bid_data = deepcopy(test_bids[0])
        bid_data.update({
            "tenderers": [test_organization],
            "documents": []
        })

        self.bid_data_wo_docs = bid_data

        super(TenderBidBatchDocumentsWithDSResourceTest, self).setUp()


class TenderBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseESCOContentWebTest,
):
    test_bids_data = test_bids
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseESCOContentWebTest,
):
    test_bids_data = test_bids
    initial_status = "active.tendering"


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TenderBidResourceTest)
    suite.addTest(TenderBidFeaturesResourceTest)
    suite.addTest(TenderBidDocumentResourceTest)
    suite.addTest(TenderBidDocumentWithDSResourceTest)
    suite.addTest(TenderBidDocumentWithoutDSResourceTest)
    suite.addTest(TenderBidBatchDocumentsWithDSResourceTest)
    suite.addTest(TenderBidRequirementResponseResourceTest)
    suite.addTest(TenderBidRequirementResponseEvidenceResourceTest)
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
