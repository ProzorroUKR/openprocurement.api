import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.award import (
    TenderAwardPendingResourceTestCase,
)
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    bid_activate_with_cancelled_tenderer_criterion,
    bid_Administrator_change,
    bid_proposal_doc,
    create_one_tender_bid_document_json_bulk,
    create_tender_bid,
    create_tender_bid_document_active_qualification,
    create_tender_bid_document_invalid_award_status,
    create_tender_bid_document_json,
    create_tender_bid_document_json_bulk,
    create_tender_bid_document_with_award_json,
    create_tender_bid_document_with_award_json_bulk,
    create_tender_bid_invalid,
    create_tender_bid_no_scale_invalid,
    create_tender_bid_with_document,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_documents,
    delete_tender_bid,
    features_bid_invalid,
    get_tender_bid,
    get_tender_bid_data_for_sign,
    get_tender_tenderers,
    not_found,
    patch_pending_bid,
    patch_tender_bid,
    patch_tender_bid_document,
    patch_tender_bid_with_another_currency,
    patch_tender_bid_with_disabled_lot_values_restriction,
    patch_tender_bid_with_disabled_value_restriction,
    patch_tender_bid_with_exceeded_lot_values,
    patch_tender_lot_values_any_order,
    post_tender_bid_with_another_currency,
    post_tender_bid_with_disabled_lot_values_restriction,
    post_tender_bid_with_disabled_value_restriction,
    post_tender_bid_with_exceeded_lot_values,
    put_tender_bid_document_json,
    update_tender_bid_pmr_related_tenderer,
    update_tender_rr,
    update_tender_rr_evidence_id,
)
from openprocurement.tender.core.tests.base import test_language_criteria
from openprocurement.tender.core.tests.utils import set_bid_items, set_bid_responses
from openprocurement.tender.openeu.tests.bid import (
    CreateBidMixin,
    TenderBidRequirementResponseEvidenceTestMixin,
    TenderBidRequirementResponseTestMixin,
)
from openprocurement.tender.openua.tests.bid_blanks import (
    patch_bid_during_qualification_forbidden,
    patch_bid_during_qualification_with_24h_milestone,
)
from openprocurement.tender.requestforproposal.tests.base import (
    TenderContentWebTest,
    test_tender_rfp_bids,
    test_tender_rfp_data_no_auction,
    test_tender_rfp_features_data,
    test_tender_rfp_lots,
    test_tender_rfp_lots_no_min_step,
    test_tender_rfp_simple_data,
    test_tender_rfp_supplier,
)
from openprocurement.tender.requestforproposal.tests.bid_blanks import (
    features_bid,
    patch_bid_multi_currency,
    patch_tender_bid_with_disabled_lot_values_currency_equality,
    patch_tender_bid_with_disabled_value_currency_equality,
    patch_tender_with_bids_lots_none,
    post_bid_multi_currency,
    post_tender_bid_with_disabled_lot_values_currency_equality,
    post_tender_bid_with_disabled_value_currency_equality,
    update_tender_bid_pmr_related_doc,
)


class TenderBidResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_create_tender_bid = snitch(create_tender_bid)
    test_patch_tender_bid = snitch(patch_tender_bid)
    test_get_tender_bid = snitch(get_tender_bid)
    test_get_tender_bid_data_for_sign = snitch(get_tender_bid_data_for_sign)
    test_delete_tender_bid = snitch(delete_tender_bid)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_create_tender_bid_no_scale_invalid = snitch(create_tender_bid_no_scale_invalid)


class Tender2LotBidResourceTest(TenderContentWebTest):
    initial_lots = 2 * test_tender_rfp_lots
    test_bids_data = test_tender_rfp_bids
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)
    test_patch_tender_lot_values_any_order = snitch(patch_tender_lot_values_any_order)
    test_post_tender_bid_with_exceeded_lot_values = snitch(post_tender_bid_with_exceeded_lot_values)
    test_patch_tender_bid_with_exceeded_lot_values = snitch(patch_tender_bid_with_exceeded_lot_values)
    test_post_tender_bid_with_another_currency = snitch(post_tender_bid_with_another_currency)
    test_patch_tender_bid_with_another_currency = snitch(patch_tender_bid_with_another_currency)
    test_bid_proposal_doc = snitch(bid_proposal_doc)
    test_patch_pending_bid = snitch(patch_pending_bid)


class TenderBidFeaturesResourceTest(TenderContentWebTest):
    initial_data = test_tender_rfp_features_data
    initial_status = "active.tendering"

    test_features_bid = snitch(features_bid)
    test_features_bid_invalid = snitch(features_bid_invalid)


class TenderBidDocumentResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    guarantee_criterion = True

    def setUp(self):
        super().setUp()
        # Create bid
        bid_data = {"status": "draft", "tenderers": [test_tender_rfp_supplier], "value": {"amount": 500}}
        set_bid_items(self, bid_data)

        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )
        bid = response.json["data"]
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]

        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]

        self.rr_data = set_bid_responses(tender.get("criteria", []))

        response = self.app.post_json(
            "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(
                self.tender_id, self.bid_id, self.bid_token
            ),
            {"data": self.rr_data},
        )

        self.rr_guarantee_id = response.json["data"][0]["id"]
        self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
            {"data": {"status": "pending"}},
        )

    test_not_found = snitch(not_found)
    test_patch_tender_bid_document = snitch(patch_tender_bid_document)
    test_create_tender_bid_document_invalid_award_status = snitch(create_tender_bid_document_invalid_award_status)
    test_create_tender_bid_document_json = snitch(create_tender_bid_document_json)
    test_create_tender_bid_document_json_bulk = snitch(create_tender_bid_document_json_bulk)
    test_create_one_tender_bid_document_json_bulk = snitch(create_one_tender_bid_document_json_bulk)
    test_put_tender_bid_document_json = snitch(put_tender_bid_document_json)
    test_create_tender_bid_document_with_award_json = snitch(create_tender_bid_document_with_award_json)
    test_create_tender_bid_document_with_award_json_bulk = snitch(create_tender_bid_document_with_award_json_bulk)


class TenderBidRRResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    guarantee_criterion = True
    guarantee_criterion_data = test_language_criteria

    test_update_tender_rr = snitch(update_tender_rr)
    test_update_tender_rr_evidence_id = snitch(update_tender_rr_evidence_id)
    test_update_tender_bid_pmr_related_doc = snitch(update_tender_bid_pmr_related_doc)
    test_update_tender_bid_pmr_related_tenderer = snitch(update_tender_bid_pmr_related_tenderer)


class SimpleTenderBidDocumentResourceTest(TenderContentWebTest):
    guarantee_criterion = False
    initial_status = "active.tendering"
    initial_data = test_tender_rfp_simple_data
    test_create_tender_bid_document_active_qualification = snitch(create_tender_bid_document_active_qualification)

    def setUp(self):
        super().setUp()
        # Create bid
        bid_data = {"status": "draft", "tenderers": [test_tender_rfp_supplier], "value": {"amount": 500}}
        bid, token = self.create_bid(self.tender_id, bid_data)
        self.bid_id = bid["id"]
        self.bid_token = token
        self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
            {"data": {"status": "pending"}},
        )


class TenderBidBatchDocumentResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    bid_data_wo_docs = {"tenderers": [test_tender_rfp_supplier], "value": {"amount": 500}, "documents": []}

    test_create_tender_bid_with_document_invalid = snitch(create_tender_bid_with_document_invalid)
    test_create_tender_bid_with_document = snitch(create_tender_bid_with_document)
    test_create_tender_bid_with_documents = snitch(create_tender_bid_with_documents)


class TenderBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    TenderContentWebTest,
):
    test_bids_data = test_tender_rfp_bids
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    TenderContentWebTest,
):
    test_bids_data = test_tender_rfp_bids
    initial_status = "active.tendering"

    test_bid_activate_with_cancelled_tenderer_criterion = snitch(bid_activate_with_cancelled_tenderer_criterion)


class TenderLotsWithDisabledValueRestriction(TenderContentWebTest):
    initial_status = "active.tendering"
    test_bids_data = test_tender_rfp_bids
    initial_lots = 2 * test_tender_rfp_lots

    test_post_tender_bid_with_disabled_lot_values_restriction = snitch(
        post_tender_bid_with_disabled_lot_values_restriction
    )
    test_patch_tender_bid_with_disabled_lot_values_restriction = snitch(
        patch_tender_bid_with_disabled_lot_values_restriction
    )

    def setUp(self):
        super(TenderContentWebTest, self).setUp()
        config = deepcopy(self.initial_config)
        config.update({"hasValueRestriction": False})
        self.create_tender(config=config)


class TenderWithDisabledValueRestriction(TenderContentWebTest):
    initial_status = "active.tendering"

    test_post_tender_bid_with_disabled_value_restriction = snitch(post_tender_bid_with_disabled_value_restriction)
    test_patch_tender_bid_with_disabled_value_restriction = snitch(patch_tender_bid_with_disabled_value_restriction)

    def setUp(self):
        super(TenderContentWebTest, self).setUp()
        config = deepcopy(self.initial_config)
        config.update({"hasValueRestriction": False})
        self.create_tender(config=config)


class TenderLotsWithDisabledValueCurrencyEquality(TenderContentWebTest):
    initial_status = "active.tendering"
    test_bids_data = test_tender_rfp_bids
    initial_lots = 2 * deepcopy(test_tender_rfp_lots_no_min_step)
    initial_data = test_tender_rfp_data_no_auction

    test_post_tender_bid_with_disabled_lot_values_currency_equality = snitch(
        post_tender_bid_with_disabled_lot_values_currency_equality
    )
    test_patch_tender_bid_with_disabled_lot_values_currency_equality = snitch(
        patch_tender_bid_with_disabled_lot_values_currency_equality
    )
    test_post_bid_multi_currency = snitch(post_bid_multi_currency)
    test_patch_bid_multi_currency = snitch(patch_bid_multi_currency)

    def setUp(self):
        super(TenderContentWebTest, self).setUp()
        config = deepcopy(self.initial_config)
        config.update(
            {
                "hasAuction": False,
                "hasAwardingOrder": False,
                "hasValueRestriction": False,
                "valueCurrencyEquality": False,
            }
        )
        self.create_tender(config=config)


class TenderWithDisabledValueCurrencyEquality(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_data = test_tender_rfp_data_no_auction

    test_post_tender_bid_with_disabled_value_currency_equality = snitch(
        post_tender_bid_with_disabled_value_currency_equality
    )
    test_patch_tender_bid_with_disabled_value_currency_equality = snitch(
        patch_tender_bid_with_disabled_value_currency_equality
    )

    def setUp(self):
        super(TenderContentWebTest, self).setUp()
        config = deepcopy(self.initial_config)
        config.update(
            {
                "hasAuction": False,
                "hasAwardingOrder": False,
                "hasValueRestriction": False,
                "valueCurrencyEquality": False,
            }
        )
        self.create_tender(config=config)


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderBidDuringQualification(TenderAwardPendingResourceTestCase):
    test_patch_bid_during_qualification_forbidden = snitch(patch_bid_during_qualification_forbidden)
    test_patch_bid_during_qualification_with_24h_milestone = snitch(patch_bid_during_qualification_with_24h_milestone)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidRequirementResponseResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidRequirementResponseEvidenceResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotsWithDisabledValueRestriction))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderWithDisabledValueRestriction))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotsWithDisabledValueCurrencyEquality))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderWithDisabledValueCurrencyEquality))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
