# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17

from openprocurement.tender.belowthreshold.tests.base import test_organization, test_author
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    patch_tender_with_bids_lots_none,
    create_tender_bid_contract_data_document_json,
)
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_features_tender_data,
    test_bids,
    test_lots,
)
from openprocurement.tender.cfaua.tests.bid_blanks import (
    bids_activation_on_tender_documents,
    create_tender_bidder,
    create_tender_bidder_document,
    create_tender_biddder_invalid,
    create_tender_bid_with_all_documents,
    create_tender_bid_with_document,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_documents,
    create_tender_bid_with_eligibility_document_invalid,
    create_tender_bid_with_financial_document_invalid,
    create_tender_bid_with_qualification_document_invalid,
    create_tender_bid_with_eligibility_document,
    create_tender_bid_with_qualification_document,
    create_tender_bid_with_financial_document,
    create_tender_bid_with_financial_documents,
    create_tender_bid_with_eligibility_documents,
    create_tender_bid_with_qualification_documents,
    deleted_bid_do_not_locks_tender_in_state,
    deleted_bid_is_not_restorable,
    get_tender_tenderers,
    get_tender_bidder_document,
    get_tender_bidder_document_ds,
    features_bidder,
    features_bidder_invalid,
    put_tender_bidder_document,
    put_tender_bidder_document_private_json,
    patch_and_put_document_into_invalid_bid,
    patch_tender_bidder,
    patch_tender_bidder_document,
    patch_tender_bidder_document_private,
    download_tender_bidder_document,
    bids_invalidation_on_tender_change,
    create_tender_bidder_document_nopending,
    bid_Administrator_change,
    change_bid_document_in_qualification_st_st,
    view_bid_in_qualification_st_st,
    post_winningBid_document_in_awarded,
)
from openprocurement.tender.openua.tests.bid import (
    TenderBidRequirementResponseTestMixin,
    TenderBidRequirementResponseEvidenceTestMixin,
)
from openprocurement.tender.openeu.tests.bid_blanks import patch_tender_bidder_document_private_json, not_found


class BaseTenderLotsContentWebTest(BaseTenderContentWebTest):
    def convert_bids_for_tender_with_lots(self, bids, lots):
        for lot in lots:
            for bid in bids:
                if "value" not in bid:
                    continue
                if "lotValues" not in bid:
                    bid["lotValues"] = []
                bid["lotValues"].append({"value": bid["value"], "relatedLot": lot["id"]})
        for bid in bids:
            if "value" in bid:
                bid.pop("value")

    def setUp(self):
        super(BaseTenderLotsContentWebTest, self).setUp()


class TenderBidResourceTest(BaseTenderLotsContentWebTest):
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_lots
    test_bids_data = deepcopy(test_bids)
    author_data = test_author

    # test_delete_tender_bidder = snitch(delete_tender_bidder)    # TODO REWRITE THIS TEST
    test_create_tender_bidder = snitch(create_tender_bidder)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)
    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_create_tender_biddder_invalid = snitch(create_tender_biddder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)
    # test_get_tender_bidder = snitch(get_tender_bidder) TODO RERWRITE THIS TEST
    test_deleted_bid_do_not_locks_tender_in_state = snitch(deleted_bid_do_not_locks_tender_in_state)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)


class TenderBidFeaturesResourceTest(BaseTenderLotsContentWebTest):
    initial_data = test_features_tender_data
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_lots
    test_bids_data = deepcopy(test_bids)

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentResourceTest(BaseTenderLotsContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.tendering"
    test_bids_data = deepcopy(test_bids)
    initial_lots = test_lots

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bids
        for x in range(self.min_bids_number):
            bids_data = deepcopy(test_bids)
            self.convert_bids_for_tender_with_lots(bids_data, self.initial_lots)
            response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bids_data[0]})
            bid = response.json["data"]
            x = "" if x == 0 else x + 1
            setattr(self, "bid{}_id".format(x), bid["id"])
            setattr(self, "bid{}_token".format(x), response.json["access"]["token"])

    test_patch_and_put_document_into_invalid_bid = snitch(patch_and_put_document_into_invalid_bid)
    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending)
    test_not_found = snitch(not_found)
    test_get_tender_bidder_document = snitch(get_tender_bidder_document)
    test_create_tender_bidder_document = snitch(create_tender_bidder_document)
    test_put_tender_bidder_document = snitch(put_tender_bidder_document)
    test_patch_tender_bidder_document = snitch(patch_tender_bidder_document)
    test_patch_tender_bidder_document_private = snitch(patch_tender_bidder_document_private)
    test_download_tender_bidder_document = snitch(download_tender_bidder_document)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_patch_tender_bidder_document_private_json = snitch(patch_tender_bidder_document_private_json)
    test_put_tender_bidder_document_private_json = snitch(put_tender_bidder_document_private_json)
    test_get_tender_bidder_document_ds = snitch(get_tender_bidder_document_ds)
    test_change_bid_document_in_qualification_st_st = snitch(change_bid_document_in_qualification_st_st)
    test_view_bid_in_qualification_st_st = snitch(view_bid_in_qualification_st_st)
    test_post_winningBid_document_in_awarded = snitch(post_winningBid_document_in_awarded)
    test_create_tender_bid_contract_data_document_json = snitch(create_tender_bid_contract_data_document_json)


class TenderBidBatchDocumentsWithDSResourceTest(BaseTenderLotsContentWebTest):
    docservice = True
    initial_status = "active.tendering"

    test_bids_data = deepcopy(test_bids)
    author_data = test_bids[0]["tenderers"][0]

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


class CreateBidMixin(object):
    base_bid_status = "draft"

    def setUp(self):
        super(CreateBidMixin, self).setUp()
        # Create bids
        for x in range(self.min_bids_number):
            bids_data = deepcopy(test_bids)
            self.convert_bids_for_tender_with_lots(bids_data, self.initial_lots)
            bids_data[0]["status"] = self.base_bid_status
            response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bids_data[0]})
            bid = response.json["data"]
            x = "" if x == 0 else x + 1
            setattr(self, "bid{}_id".format(x), bid["id"])
            setattr(self, "bid{}_token".format(x), response.json["access"]["token"])

        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]


class TenderBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseTenderLotsContentWebTest,
):
    test_bids_data = test_bids
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseTenderLotsContentWebTest,
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
