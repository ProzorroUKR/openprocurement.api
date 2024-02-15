import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_features_data,
    test_tender_below_organization,
    test_tender_below_lots,
    test_tender_below_bids,
    test_tender_below_simple_data,
    test_tender_below_data,
)
from openprocurement.tender.core.tests.base import test_language_criteria
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderBidResourceTest
    create_tender_bid_invalid,
    create_tender_bid,
    patch_tender_bid,
    get_tender_bid,
    delete_tender_bid,
    get_tender_tenderers,
    bid_Administrator_change,
    create_tender_bid_no_scale_invalid,
    # TenderBidFeaturesResourceTest
    features_bid,
    features_bid_invalid,
    # TenderBidDocumentResourceTest
    not_found,
    patch_tender_bid_document,
    create_tender_bid_document_invalid_award_status,
    # TenderBidDocumentWithDSResourceTest
    create_tender_bid_document_json,
    create_tender_bid_document_json_bulk,
    create_one_tender_bid_document_json_bulk,
    put_tender_bid_document_json,
    create_tender_bid_document_with_award_json,
    create_tender_bid_document_with_award_json_bulk,
    create_tender_bid_document_active_qualification,
    # TenderBidBatchDocumentWithDSResourceTest
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
    create_tender_bid_with_documents,
    # Tender2LotBidResourceTest
    patch_tender_with_bids_lots_none,
    post_tender_bid_with_exceeded_lot_values,
    patch_tender_bid_with_exceeded_lot_values,
    bid_activate_with_cancelled_tenderer_criterion,
    update_tender_bid_pmr_related_doc,
    update_tender_rr_evidence_id,
    update_tender_bid_pmr_related_tenderer,
    patch_tender_lot_values_any_order,
    # TenderLotsWithDisabledValueRestriction
    post_tender_bid_with_disabled_lot_values_restriction,
    patch_tender_bid_with_disabled_lot_values_restriction,
    # TenderWithDisabledValueRestriction
    post_tender_bid_with_disabled_value_restriction,
    patch_tender_bid_with_disabled_value_restriction,
    post_tender_bid_with_another_currency,
    patch_tender_bid_with_another_currency,
    # TenderLotsWithDisabledValueCurrencyEquality
    post_tender_bid_with_disabled_lot_values_currency_equality,
    patch_tender_bid_with_disabled_lot_values_currency_equality,
    # TenderWithDisabledValueCurrencyEquality
    post_tender_bid_with_disabled_value_currency_equality,
    patch_tender_bid_with_disabled_value_currency_equality,
)
from openprocurement.tender.openeu.tests.bid import CreateBidMixin
from openprocurement.tender.openeu.tests.bid import (
    TenderBidRequirementResponseTestMixin,
    TenderBidRequirementResponseEvidenceTestMixin,
)


class TenderBidResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_create_tender_bid = snitch(create_tender_bid)
    test_patch_tender_bid = snitch(patch_tender_bid)
    test_get_tender_bid = snitch(get_tender_bid)
    test_delete_tender_bid = snitch(delete_tender_bid)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_create_tender_bid_no_scale_invalid = snitch(create_tender_bid_no_scale_invalid)


class Tender2LotBidResourceTest(TenderContentWebTest):
    initial_lots = 2 * test_tender_below_lots
    test_bids_data = test_tender_below_bids
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)
    test_patch_tender_lot_values_any_order = snitch(patch_tender_lot_values_any_order)
    test_post_tender_bid_with_exceeded_lot_values = snitch(post_tender_bid_with_exceeded_lot_values)
    test_patch_tender_bid_with_exceeded_lot_values = snitch(patch_tender_bid_with_exceeded_lot_values)
    test_post_tender_bid_with_another_currency = snitch(post_tender_bid_with_another_currency)
    test_patch_tender_bid_with_another_currency = snitch(patch_tender_bid_with_another_currency)


class TenderBidFeaturesResourceTest(TenderContentWebTest):
    initial_data = test_tender_below_features_data
    initial_status = "active.tendering"

    test_features_bid = snitch(features_bid)
    test_features_bid_invalid = snitch(features_bid_invalid)


class TenderBidDocumentResourceTest(TenderContentWebTest):
    docservice = True
    initial_status = "active.tendering"
    guarantee_criterion = True

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": {"status": "draft", "tenderers": [test_tender_below_organization], "value": {"amount": 500}}},
        )
        bid = response.json["data"]
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]

        requirement = self.app.get("/tenders/{}".format(self.tender_id)).json["data"]["criteria"][0][
            "requirementGroups"
        ][0]["requirements"][0]

        self.rr_data = [
            {
                "title": "Requirement response",
                "description": "some description",
                "requirement": {
                    "id": requirement["id"],
                    "title": requirement["title"],
                },
                "value": "True",
            }
        ]

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


class TenderBidRRResourceTest(TenderContentWebTest):
    docservice = True
    initial_status = "active.tendering"
    guarantee_criterion = True
    guarantee_criterion_data = test_language_criteria

    test_update_tender_rr_evidence_id = snitch(update_tender_rr_evidence_id)
    test_update_tender_bid_pmr_related_doc = snitch(update_tender_bid_pmr_related_doc)
    test_update_tender_bid_pmr_related_tenderer = snitch(update_tender_bid_pmr_related_tenderer)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_create_tender_bid_document_json = snitch(create_tender_bid_document_json)
    test_create_tender_bid_document_json_bulk = snitch(create_tender_bid_document_json_bulk)
    test_create_one_tender_bid_document_json_bulk = snitch(create_one_tender_bid_document_json_bulk)
    test_put_tender_bid_document_json = snitch(put_tender_bid_document_json)
    test_create_tender_bid_document_with_award_json = snitch(create_tender_bid_document_with_award_json)
    test_create_tender_bid_document_with_award_json_bulk = snitch(create_tender_bid_document_with_award_json_bulk)


class SimpleTenderBidDocumentResourceTest(TenderContentWebTest):
    docservice = True
    guarantee_criterion = False
    initial_status = "active.tendering"
    initial_data = test_tender_below_simple_data
    test_create_tender_bid_document_active_qualification = snitch(create_tender_bid_document_active_qualification)

    def setUp(self):
        super(SimpleTenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": {"status": "draft", "tenderers": [test_tender_below_organization], "value": {"amount": 500}}},
        )
        bid = response.json["data"]
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]
        self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
            {"data": {"status": "pending"}},
        )


class TenderBidBatchDocumentWithDSResourceTest(TenderContentWebTest):
    docservice = True
    initial_status = "active.tendering"
    bid_data_wo_docs = {"tenderers": [test_tender_below_organization], "value": {"amount": 500}, "documents": []}

    test_create_tender_bid_with_document_invalid = snitch(create_tender_bid_with_document_invalid)
    test_create_tender_bid_with_document = snitch(create_tender_bid_with_document)
    test_create_tender_bid_with_documents = snitch(create_tender_bid_with_documents)


class TenderBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    TenderContentWebTest,
):
    test_bids_data = test_tender_below_bids
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    TenderContentWebTest,
):
    test_bids_data = test_tender_below_bids
    initial_status = "active.tendering"

    test_bid_activate_with_cancelled_tenderer_criterion = snitch(bid_activate_with_cancelled_tenderer_criterion)


class TenderLotsWithDisabledValueRestriction(TenderContentWebTest):
    initial_status = "active.tendering"
    test_bids_data = test_tender_below_bids
    initial_lots = 2 * test_tender_below_lots

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
    test_bids_data = test_tender_below_bids
    initial_lots = 2 * test_tender_below_lots
    test_tender_below_data_no_auction = deepcopy(test_tender_below_data)
    del test_tender_below_data_no_auction["minimalStep"]
    initial_data = test_tender_below_data_no_auction

    test_post_tender_bid_with_disabled_lot_values_currency_equality = snitch(
        post_tender_bid_with_disabled_lot_values_currency_equality
    )
    test_patch_tender_bid_with_disabled_lot_values_currency_equality = snitch(
        patch_tender_bid_with_disabled_lot_values_currency_equality
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


class TenderWithDisabledValueCurrencyEquality(TenderContentWebTest):
    initial_status = "active.tendering"
    test_tender_below_data_no_auction = deepcopy(test_tender_below_data)
    del test_tender_below_data_no_auction["minimalStep"]
    initial_data = test_tender_below_data_no_auction

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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidRequirementResponseResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidRequirementResponseEvidenceResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotsWithDisabledValueRestriction))
    suite.addTest(unittest.makeSuite(TenderWithDisabledValueRestriction))
    suite.addTest(unittest.makeSuite(TenderLotsWithDisabledValueCurrencyEquality))
    suite.addTest(unittest.makeSuite(TenderWithDisabledValueCurrencyEquality))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
