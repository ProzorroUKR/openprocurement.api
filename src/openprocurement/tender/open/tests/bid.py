# -*- coding: utf-8 -*-
import unittest
from mock import patch
from datetime import timedelta
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.base import test_exclusion_criteria
from openprocurement.tender.belowthreshold.tests.utils import set_bid_lotvalues
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
    test_tender_below_author,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    not_found,
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
)

from openprocurement.tender.open.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_open_data,
    test_tender_open_features_data,
    test_tender_open_bids,
)
from openprocurement.tender.open.tests.bid_blanks import (
    create_tender_biddder_invalid,
    create_tender_bidder,
    create_bid_after_removing_lot,
    patch_tender_bidder,
    get_tender_bidder,
    delete_tender_bidder,
    deleted_bid_is_not_restorable,
    deleted_bid_do_not_locks_tender_in_state,
    get_tender_tenderers,
    bid_Administrator_change,
    draft1_bid,
    draft2_bids,
    bids_invalidation_on_tender_change,
    bids_activation_on_tender_documents,
    create_tender_bid_no_scale_invalid,
    create_tender_bid_with_scale_not_required,
    create_tender_bid_no_scale,
    features_bidder,
    features_bidder_invalid,
    create_tender_bidder_document,
    put_tender_bidder_document,
    patch_tender_bidder_document,
    create_tender_bidder_document_nopending,
    create_tender_bidder_document_json,
    put_tender_bidder_document_json,
    patch_tender_bidder_document_json,
    tender_bidder_confidential_document,
    create_tender_bidder_document_nopending_json,
    create_bid_requirement_response,
    patch_bid_requirement_response,
    get_bid_requirement_response,
    patch_bid_with_responses,
    bid_activate_with_cancelled_tenderer_criterion,
    bid_invalidation_after_requirement_put,
    create_bid_requirement_response_evidence,
    patch_bid_requirement_response_evidence,
    get_bid_requirement_response_evidence,
    bid_activate,
    doc_date_modified,
    patch_tender_draft_bidder,
    patch_tender_with_bids_lots_none,
    patch_tender_bidder_decimal_problem,
    create_tender_bidder_value_greater_then_lot,
)


class TenderBidResourceTestMixin:
    test_create_tender_biddder_invalid = snitch(create_tender_biddder_invalid)
    test_create_tender_bidder = snitch(create_tender_bidder)
    test_create_tender_bidder_value_greater_then_lot = snitch(create_tender_bidder_value_greater_then_lot)
    test_patch_tender_bidder = snitch(patch_tender_bidder)
    test_patch_tender_draft_bidder = snitch(patch_tender_draft_bidder)
    test_get_tender_bidder = snitch(get_tender_bidder)
    test_delete_tender_bidder = snitch(delete_tender_bidder)
    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_deleted_bid_do_not_locks_tender_in_state = snitch(deleted_bid_do_not_locks_tender_in_state)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)
    test_create_tender_bid_no_scale_invalid = snitch(create_tender_bid_no_scale_invalid)
    test_create_tender_bid_with_scale_not_required = snitch(create_tender_bid_with_scale_not_required)
    test_create_tender_bid_no_scale = snitch(create_tender_bid_no_scale)


@patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.models.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
class TenderBidDocumentResourceTestMixin:
    test_create_tender_bidder_document = snitch(create_tender_bidder_document)
    test_put_tender_bidder_document = snitch(put_tender_bidder_document)
    test_patch_tender_bidder_document = snitch(patch_tender_bidder_document)
    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending)


@patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.models.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
class TenderBidRequirementResponseTestMixin:
    test_create_bid_requirement_response = snitch(create_bid_requirement_response)
    test_patch_bid_requirement_response = snitch(patch_bid_requirement_response)
    test_get_bid_requirement_response = snitch(get_bid_requirement_response)
    test_patch_bid_with_responses = snitch(patch_bid_with_responses)

    initial_criteria = test_exclusion_criteria

    @patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.models.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
    def setUp(self):
        super(TenderBidRequirementResponseTestMixin, self).setUp()
        response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
        criteria = response.json["data"]
        requirement = criteria[0]["requirementGroups"][0]["requirements"][0]
        self.requirement_id = requirement["id"]
        self.requirement_title = requirement["title"]
        requirement = criteria[1]["requirementGroups"][0]["requirements"][0]
        self.requirement_2_id = requirement["id"]
        self.requirement_2_title = requirement["title"]


@patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.models.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
class TenderBidRequirementResponseEvidenceTestMixin:
    docservice = True

    test_create_bid_requirement_response_evidence = snitch(create_bid_requirement_response_evidence)
    test_patch_bid_requirement_response_evidence = snitch(patch_bid_requirement_response_evidence)
    test_get_bid_requirement_response_evidence = snitch(get_bid_requirement_response_evidence)
    test_bid_activate = snitch(bid_activate)
    test_bid_activate_with_cancelled_tenderer_criterion = snitch(bid_activate_with_cancelled_tenderer_criterion)

    initial_criteria = test_exclusion_criteria

    @patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.models.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
    def setUp(self):
        super(TenderBidRequirementResponseEvidenceTestMixin, self).setUp()
        response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
        criteria = response.json["data"]
        requirement = criteria[0]["requirementGroups"][0]["requirements"][0]
        self.requirement_id = requirement["id"]
        self.requirement_title = requirement["title"]

        request_path = "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(
            self.tender_id, self.bid_id, self.bid_token)

        rr_data = [{
            "title": "Requirement response",
            "description": "some description",
            "requirement": {
                "id": self.requirement_id,
                "title": self.requirement_title,
            },
            "value": True,
        }]

        response = self.app.post_json(request_path, {"data": rr_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.rr_id = response.json["data"][0]["id"]

        response = self.app.post_json(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(
                self.tender_id, self.bid_id, self.bid_token),
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


class CreateBidMixin(object):
    base_bid_status = "active"

    def setUp(self):
        super(CreateBidMixin, self).setUp()
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
    docservice = True
    initial_data = test_tender_open_data
    initial_lots = test_tender_below_lots
    initial_status = "active.tendering"
    test_bids_data = test_tender_open_bids
    author_data = test_tender_below_author

    test_draft1_bid = snitch(draft1_bid)
    test_draft2_bids = snitch(draft2_bids)


class TenderBidDecimalResourceTest(BaseTenderUAContentWebTest):
    docservice = True
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
        super(TenderBidDecimalResourceTest, self).setUp()

    test_patch_tender_bidder_decimal_problem = snitch(patch_tender_bidder_decimal_problem)


class Tender2LotBidResourceTest(BaseTenderUAContentWebTest):
    docservice = True
    initial_data = test_tender_open_data
    test_bids_data = test_tender_open_bids
    initial_lots = 2 * test_tender_below_lots
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)
    test_create_bid_after_removing_lot = snitch(create_bid_after_removing_lot)


class TenderBidFeaturesResourceTest(BaseTenderUAContentWebTest):
    docservice = True
    initial_data = test_tender_open_features_data
    initial_lots = test_tender_below_lots
    initial_status = "active.tendering"
    test_bids_data = test_tender_open_bids

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentResourceTest(CreateBidMixin, BaseTenderUAContentWebTest):
    docservice = True
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots
    test_bids_data = test_tender_open_bids
    author_data = test_tender_below_author

    test_not_found = snitch(not_found)


class TenderBidActivateDocumentTest(CreateBidMixin, BaseTenderUAContentWebTest):
    docservice = True
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots
    test_bids_data = test_tender_open_bids
    author_data = test_tender_below_author
    base_bid_status = "draft"
    test_doc_date_modified = snitch(doc_date_modified)


class TenderBidDocumentWithDSResourceTestMixin:
    docservice = True
    test_create_tender_bidder_document_json = snitch(create_tender_bidder_document_json)
    test_put_tender_bidder_document_json = snitch(put_tender_bidder_document_json)
    test_patch_tender_bidder_document = snitch(patch_tender_bidder_document_json)
    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending_json)
    test_tender_bidder_confidential_document = snitch(tender_bidder_confidential_document)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentWithDSResourceTestMixin, TenderBidDocumentResourceTest):
    docservice = True
    initial_lots = test_tender_below_lots


class TenderBidderBatchDocumentWithDSResourceTest(BaseTenderUAContentWebTest):
    docservice = True
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
    docservice = True
    initial_data = test_tender_open_data
    initial_lots = test_tender_below_lots
    base_bid_status = "draft"
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseTenderUAContentWebTest,
):
    docservice = True
    initial_data = test_tender_open_data
    initial_lots = test_tender_below_lots
    base_bid_status = "draft"
    initial_status = "active.tendering"

    test_bid_invalidation_after_requirement_put = snitch(bid_invalidation_after_requirement_put)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidRequirementResponseResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidRequirementResponseEvidenceResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
