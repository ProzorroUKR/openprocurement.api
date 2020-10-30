# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17

from openprocurement.tender.belowthreshold.tests.base import test_organization, test_author

from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderBidBatchDocumentWithDSResourceTest
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
    # Tender2LotBidResourceTest
    patch_tender_with_bids_lots_none,
    create_tender_bid_contract_data_document_json,
)

from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_features_tender_data,
    test_bids,
    test_lots,
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
    not_found,
    get_tender_bidder_document,
    create_tender_bidder_document,
    put_tender_bidder_document,
    patch_tender_bidder_document,
    patch_tender_bidder_document_private,
    patch_and_put_document_into_invalid_bid,
    download_tender_bidder_document,
    create_tender_bidder_document_nopending,
    # TenderBidFeaturesResourceTest
    features_bidder,
    features_bidder_invalid,
    # TenderBidResourceTest
    create_tender_biddder_invalid,
    create_tender_bidder,
    patch_tender_bidder,
    get_tender_bidder,
    delete_tender_bidder,
    deleted_bid_is_not_restorable,
    deleted_bid_do_not_locks_tender_in_state,
    get_tender_tenderers,
    bid_Administrator_change,
    bids_invalidation_on_tender_change,
    bids_activation_on_tender_documents,
    # TenderBidBatchDocumentsWithDSResourceTest
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
)

from openprocurement.tender.openua.tests.bid_blanks import (
    create_tender_bid_no_scale_invalid,
    create_tender_bid_with_scale_not_required,
    create_tender_bid_no_scale,
)


class CreateBidMixin(object):
    base_bid_status = "draft"

    def setUp(self):
        super(CreateBidMixin, self).setUp()
        # Create bid
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker', ''))
        bid_data = self.test_bids_data[0].copy()
        bid_data["status"] = self.base_bid_status
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
        bid = response.json["data"]
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]


class TenderBidResourceTestMixin(object):
    test_create_tender_bidder = snitch(create_tender_bidder)
    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)


class Tender2BidResourceTestMixin(object):
    test_create_tender_biddder_invalid = snitch(create_tender_biddder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)
    test_get_tender_bidder = snitch(get_tender_bidder)
    test_deleted_bid_do_not_locks_tender_in_state = snitch(deleted_bid_do_not_locks_tender_in_state)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_create_tender_bid_no_scale_invalid = snitch(create_tender_bid_no_scale_invalid)
    test_create_tender_bid_with_scale_not_required = snitch(create_tender_bid_with_scale_not_required)
    test_create_tender_bid_no_scale = snitch(create_tender_bid_no_scale)


class TenderBidDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_get_tender_bidder_document = snitch(get_tender_bidder_document)
    test_create_tender_bidder_document = snitch(create_tender_bidder_document)
    test_put_tender_bidder_document = snitch(put_tender_bidder_document)
    test_patch_tender_bidder_document = snitch(patch_tender_bidder_document)
    test_patch_tender_bidder_document_private = snitch(patch_tender_bidder_document_private)
    test_download_tender_bidder_document = snitch(download_tender_bidder_document)


class TenderBidResourceTest(BaseTenderContentWebTest, TenderBidResourceTestMixin, Tender2BidResourceTestMixin):
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_bids  # TODO: change attribute identifier
    author_data = test_author

    test_delete_tender_bidder = snitch(delete_tender_bidder)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change)


class Tender2LotBidResourceTest(BaseTenderContentWebTest):
    test_bids_data = test_bids
    initial_lots = 2 * test_lots
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)


class TenderBidFeaturesResourceTest(BaseTenderContentWebTest):
    initial_data = test_features_tender_data
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_bids  # TODO: change attribute identificator

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentResourceTest(BaseTenderContentWebTest, TenderBidDocumentResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.tendering"
    test_bids_data = test_bids  # TODO: change attribute identificator

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


class TenderBidBatchDocumentsWithDSResourceTest(BaseTenderContentWebTest):
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
        self.bid_data_wo_docs = {
            "tenderers": [test_organization],
            "value": {"amount": 500},
            "selfQualified": True,
            "documents": [],
        }
        if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
            self.bid_data_wo_docs["selfEligible"] = True

        super(TenderBidBatchDocumentsWithDSResourceTest, self).setUp()


class TenderBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseTenderContentWebTest,
):
    test_bids_data = test_bids
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseTenderContentWebTest,
):
    test_bids_data = test_bids
    initial_status = "active.tendering"


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidBatchDocumentsWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidRequirementResponseResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidRequirementResponseEvidenceResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
