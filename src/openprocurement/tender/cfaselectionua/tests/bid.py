# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderBidResourceTest
    patch_tender_with_bids_lots_none,
    create_tender_bid_contract_data_document_json,
)

from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_organization,
    test_lots,
    test_agreement_features,
    test_bids,
)
from openprocurement.tender.openua.tests.bid import (
    TenderBidRequirementResponseTestMixin,
    TenderBidRequirementResponseEvidenceTestMixin,
)
from openprocurement.tender.cfaselectionua.tests.bid_blanks import (
    # TenderBidResourceTest
    create_tender_bid_invalid,
    create_tender_bid,
    patch_tender_bid,
    get_tender_bid,
    delete_tender_bid,
    get_tender_tenderers,
    bid_Administrator_change,
    # TenderBidFeaturesResourceTest
    features_bid,
    features_bid_invalid,
    patch_features_bid_invalid,
    # TenderBidDocumentResourceTest
    not_found,
    create_tender_bid_document,
    put_tender_bid_document,
    patch_tender_bid_document,
    create_tender_bid_document_nopending,
    # TenderBidDocumentWithDSResourceTest
    create_tender_bid_document_json,
    put_tender_bid_document_json,
    # TenderBidBatchDocumentWithDSResourceTest
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
    create_tender_bid_with_documents,
)


class CreateBidMixin(object):
    base_bid_status = "draft"
    def setUp(self):
        super(CreateBidMixin, self).setUp()
        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {
                "data": {
                    "status": self.base_bid_status,
                    "tenderers": [test_organization],
                    "lotValues": [{"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]}],
                }
            },
        )
        bid = response.json["data"]
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]


class TenderBidResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_lots = deepcopy(test_lots)
    test_bids_data = deepcopy(test_bids)

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_create_tender_bid = snitch(create_tender_bid)
    test_patch_tender_bid = snitch(patch_tender_bid)
    test_get_tender_bid = snitch(get_tender_bid)
    test_delete_tender_bid = snitch(delete_tender_bid)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)


class TenderBidFeaturesResourceTest(TenderContentWebTest):
    initial_agreement = deepcopy(test_agreement_features)
    initial_lots = deepcopy(test_lots)
    initial_status = "active.tendering"

    test_features_bid = snitch(features_bid)
    test_features_bid_invalid = snitch(features_bid_invalid)
    test_patch_features_bid_invalid = snitch(patch_features_bid_invalid)

    def setUp(self):
        super(TenderBidFeaturesResourceTest, self).setUp()
        tender = self.db.get(self.tender_id)
        agreement = test_agreement_features
        agreement["contracts"][0]["parameters"] = [
            {"code": "OCDS-123454-AIR-INTAKE", "value": 0.1},
            {"code": "OCDS-123454-YEARS", "value": 0.1},
        ]
        agreement["contracts"][1]["parameters"] = [
            {"code": "OCDS-123454-AIR-INTAKE", "value": 0.15},
            {"code": "OCDS-123454-YEARS", "value": 0.15},
        ]
        agreement["id"] = tender["agreements"][0]["id"]
        tender["agreements"] = [agreement]
        self.db.save(tender)


class TenderBidDocumentResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_lots = deepcopy(test_lots)

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {
                "data": {
                    "tenderers": [test_organization],
                    "lotValues": [{"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]}],
                }
            },
        )
        bid = response.json["data"]
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]

    test_not_found = snitch(not_found)
    test_create_tender_bid_document = snitch(create_tender_bid_document)
    test_put_tender_bid_document = snitch(put_tender_bid_document)
    test_patch_tender_bid_document = snitch(patch_tender_bid_document)
    test_create_tender_bid_document_nopending = snitch(create_tender_bid_document_nopending)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_create_tender_bid_document_json = snitch(create_tender_bid_document_json)
    test_put_tender_bid_document_json = snitch(put_tender_bid_document_json)
    test_create_tender_bid_contract_data_document_json = snitch(create_tender_bid_contract_data_document_json)



class TenderBidBatchDocumentWithDSResourceTest(TenderContentWebTest):
    docservice = True
    initial_lots = deepcopy(test_lots)
    initial_status = "active.tendering"
    bid_data_wo_docs = {"tenderers": [test_organization], "value": {"amount": 500}, "documents": []}

    test_create_tender_bid_with_document_invalid = snitch(create_tender_bid_with_document_invalid)
    test_create_tender_bid_with_document = snitch(create_tender_bid_with_document)
    test_create_tender_bid_with_documents = snitch(create_tender_bid_with_documents)


class TenderBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    TenderContentWebTest,
):
    initial_lots = deepcopy(test_lots)
    test_bids_data = test_bids
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    TenderContentWebTest,
):
    initial_lots = deepcopy(test_lots)
    test_bids_data = test_bids
    initial_status = "active.tendering"


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
