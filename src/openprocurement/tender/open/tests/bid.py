import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_lots,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    bid_proposal_doc,
    create_tender_bid_with_document,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_documents,
    not_found,
    patch_pending_bid,
    patch_tender_bid_with_disabled_lot_values_restriction,
    post_tender_bid_with_disabled_lot_values_restriction,
)
from openprocurement.tender.belowthreshold.tests.utils import set_bid_lotvalues
from openprocurement.tender.core.tests.base import test_exclusion_criteria
from openprocurement.tender.open.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_open_bids,
    test_tender_open_data,
    test_tender_open_features_data,
)
from openprocurement.tender.open.tests.bid_blanks import (
    bid_activate,
    bid_activate_with_cancelled_tenderer_criterion,
    bid_Administrator_change,
    bid_invalidation_after_req_response_patch,
    bid_invalidation_after_requirement_put,
    bids_activation_on_tender_documents,
    bids_invalidation_on_tender_change,
    create_bid_after_removing_lot,
    create_bid_requirement_response,
    create_bid_requirement_response_deprecated,
    create_bid_requirement_response_evidence,
    create_tender_bid_no_scale_invalid,
    create_tender_biddder_invalid,
    create_tender_bidder,
    create_tender_bidder_document_json,
    create_tender_bidder_document_nopending_json,
    create_tender_bidder_value_greater_then_lot,
    delete_tender_bidder,
    doc_date_modified,
    draft1_bid,
    draft2_bids,
    features_bidder,
    features_bidder_invalid,
    get_bid_requirement_response,
    get_bid_requirement_response_evidence,
    get_tender_bid_data_for_sign,
    get_tender_bidder,
    get_tender_tenderers,
    patch_bid_requirement_response,
    patch_bid_requirement_response_evidence,
    patch_bid_with_responses,
    patch_tender_bid_with_disabled_value_restriction,
    patch_tender_bidder,
    patch_tender_bidder_decimal_problem,
    patch_tender_bidder_document_json,
    patch_tender_draft_bidder,
    patch_tender_with_bids_lots_none,
    post_tender_bid_with_disabled_value_restriction,
    put_tender_bidder_document_json,
    tender_bidder_confidential_document,
)
from openprocurement.tender.openua.tests.bid_blanks import bids_related_product


class TenderBidResourceTestMixin:
    test_create_tender_biddder_invalid = snitch(create_tender_biddder_invalid)
    test_create_tender_bidder = snitch(create_tender_bidder)
    test_create_tender_bidder_value_greater_then_lot = snitch(create_tender_bidder_value_greater_then_lot)
    test_patch_tender_bidder = snitch(patch_tender_bidder)
    test_patch_tender_draft_bidder = snitch(patch_tender_draft_bidder)
    test_get_tender_bidder = snitch(get_tender_bidder)
    test_delete_tender_bidder = snitch(delete_tender_bidder)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)
    test_create_tender_bid_no_scale_invalid = snitch(create_tender_bid_no_scale_invalid)
    test_bid_proposal_doc = snitch(bid_proposal_doc)
    test_patch_pending_bid = snitch(patch_pending_bid)
    test_get_tender_bid_data_for_sign = snitch(get_tender_bid_data_for_sign)


class TenderBidRequirementResponseTestMixin:
    test_create_bid_requirement_response = snitch(create_bid_requirement_response)
    test_patch_bid_requirement_response = snitch(patch_bid_requirement_response)
    test_create_bid_requirement_response_deprecated = snitch(create_bid_requirement_response_deprecated)
    test_get_bid_requirement_response = snitch(get_bid_requirement_response)
    test_patch_bid_with_responses = snitch(patch_bid_with_responses)

    initial_criteria = test_exclusion_criteria

    def setUp(self):
        super().setUp()
        response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
        criteria = response.json["data"]
        requirement = criteria[0]["requirementGroups"][0]["requirements"][0]
        self.requirement_id = requirement["id"]
        self.requirement_title = requirement["title"]
        requirement = criteria[1]["requirementGroups"][0]["requirements"][0]
        self.requirement_2_id = requirement["id"]
        self.requirement_2_title = requirement["title"]


class TenderBidRequirementResponseEvidenceTestMixin:

    test_create_bid_requirement_response_evidence = snitch(create_bid_requirement_response_evidence)
    test_patch_bid_requirement_response_evidence = snitch(patch_bid_requirement_response_evidence)
    test_get_bid_requirement_response_evidence = snitch(get_bid_requirement_response_evidence)
    test_bid_activate = snitch(bid_activate)
    test_bid_activate_with_cancelled_tenderer_criterion = snitch(bid_activate_with_cancelled_tenderer_criterion)

    initial_criteria = test_exclusion_criteria

    def setUp(self):
        super().setUp()
        response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
        criteria = response.json["data"]
        requirement = criteria[0]["requirementGroups"][0]["requirements"][0]
        self.requirement_id = requirement["id"]
        self.requirement_title = requirement["title"]

        request_path = "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(
            self.tender_id, self.bid_id, self.bid_token
        )

        rr_data = [
            {
                "title": "Requirement response",
                "description": "some description",
                "requirement": {
                    "id": self.requirement_id,
                    "title": self.requirement_title,
                },
                "value": True,
            }
        ]

        response = self.app.post_json(request_path, {"data": rr_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.rr_id = response.json["data"][0]["id"]

        response = self.app.post_json(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
            {
                "data": {
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.doc_id = response.json["data"]["id"]


class CreateBidMixin:
    base_bid_status = "pending"

    def setUp(self):
        super().setUp()
        bid_data = deepcopy(test_tender_open_bids[0])
        set_bid_lotvalues(bid_data, self.initial_lots)
        bid_data["status"] = self.base_bid_status

        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )
        bid = response.json["data"]
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]


class TenderBidResourceTest(BaseTenderUAContentWebTest, TenderBidResourceTestMixin):
    initial_data = test_tender_open_data
    initial_lots = test_tender_below_lots
    initial_status = "active.tendering"
    test_bids_data = test_tender_open_bids
    author_data = test_tender_below_author

    test_draft1_bid = snitch(draft1_bid)
    test_draft2_bids = snitch(draft2_bids)
    test_bids_related_product = snitch(bids_related_product)


class TenderBidDecimalResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_open_data
    initial_lots = test_tender_below_lots
    initial_status = "active.tendering"
    test_bids_data = test_tender_open_bids
    author_data = test_tender_below_author

    def setUp(self):
        self.initial_lots = deepcopy(self.initial_lots)
        test_amount = 319400.52
        self.initial_lots[0]["value"]["amount"] = test_amount
        self.initial_lots[0]["minimalStep"]["amount"] = test_amount / 100
        super().setUp()

    test_patch_tender_bidder_decimal_problem = snitch(patch_tender_bidder_decimal_problem)


class Tender2LotBidResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_open_data
    test_bids_data = test_tender_open_bids
    initial_lots = 2 * test_tender_below_lots
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)
    test_create_bid_after_removing_lot = snitch(create_bid_after_removing_lot)
    test_post_tender_bid_with_disabled_lot_values_restriction = snitch(
        post_tender_bid_with_disabled_lot_values_restriction
    )
    test_patch_tender_bid_with_disabled_lot_values_restriction = snitch(
        patch_tender_bid_with_disabled_lot_values_restriction
    )


class TenderBidFeaturesResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_open_features_data
    initial_lots = test_tender_below_lots
    initial_status = "active.tendering"
    test_bids_data = test_tender_open_bids

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentResourceTestMixin:
    test_create_tender_bidder_document_json = snitch(create_tender_bidder_document_json)
    test_put_tender_bidder_document_json = snitch(put_tender_bidder_document_json)
    test_patch_tender_bidder_document = snitch(patch_tender_bidder_document_json)
    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending_json)
    test_tender_bidder_confidential_document = snitch(tender_bidder_confidential_document)


class TenderBidDocumentResourceTest(CreateBidMixin, TenderBidDocumentResourceTestMixin, BaseTenderUAContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots
    test_bids_data = test_tender_open_bids
    author_data = test_tender_below_author

    test_not_found = snitch(not_found)


class TenderBidActivateDocumentTest(CreateBidMixin, BaseTenderUAContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots
    test_bids_data = test_tender_open_bids
    author_data = test_tender_below_author
    base_bid_status = "draft"
    test_doc_date_modified = snitch(doc_date_modified)


class TenderBidderBatchDocumentResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots
    test_bids_data = test_tender_open_bids
    bid_data_wo_docs = {
        "tenderers": [test_tender_below_organization],
        "value": {"amount": 500},
        "selfEligible": True,
        "selfQualified": True,
        "documents": [],
    }

    create_tender_bid_with_document_invalid = snitch(create_tender_bid_with_document_invalid)
    create_tender_bid_with_document = snitch(create_tender_bid_with_document)
    create_tender_bid_with_documents = snitch(create_tender_bid_with_documents)


class TenderBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseTenderUAContentWebTest,
):
    initial_data = test_tender_open_data
    initial_lots = test_tender_below_lots
    base_bid_status = "draft"
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseTenderUAContentWebTest,
):
    initial_data = test_tender_open_data
    initial_lots = test_tender_below_lots
    base_bid_status = "draft"
    initial_status = "active.tendering"

    test_bid_invalidation_after_requirement_put = snitch(bid_invalidation_after_requirement_put)
    test_bid_invalidation_after_req_response_patch = snitch(bid_invalidation_after_req_response_patch)


class TenderWithDisabledValueRestriction(BaseTenderUAContentWebTest):
    initial_status = "active.tendering"

    test_post_tender_bid_with_disabled_value_restriction = snitch(post_tender_bid_with_disabled_value_restriction)
    test_patch_tender_bid_with_disabled_value_restriction = snitch(patch_tender_bid_with_disabled_value_restriction)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidderBatchDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidRequirementResponseResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidRequirementResponseEvidenceResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderWithDisabledValueRestriction))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
