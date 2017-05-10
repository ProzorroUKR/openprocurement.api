# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_organization
)
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderBidDocumentResourceTest
    not_found,
    # TenderBidderBatchDocumentWithDSResourceTest
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
)

from openprocurement.tender.openua.tests.base import test_bids
from openprocurement.tender.openua.tests.bid import (
    TenderBidResourceTestMixin,
    TenderBidDocumentResourceTestMixin
)
from openprocurement.tender.openua.tests.bid_blanks import (
    # TenderBidFeaturesResourceTest
    features_bidder,
    features_bidder_invalid,
    # TenderBidDocumentWithDSResourceTest
    create_tender_bidder_document_json,
    put_tender_bidder_document_json,
)

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_features_tender_ua_data
)


class TenderBidResourceTest(BaseTenderUAContentWebTest, TenderBidResourceTestMixin):
    initial_status = 'active.tendering'
    test_bids_data = test_bids  # TODO: change attribute identifier
    author_data = test_organization


class TenderBidFeaturesResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_features_tender_ua_data
    initial_status = 'active.tendering'

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentResourceTest(BaseTenderUAContentWebTest, TenderBidDocumentResourceTestMixin):
    initial_status = 'active.tendering'
    author_data = test_organization

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'tenderers': [test_organization], "value": {"amount": 500}, 'selfEligible': True, 'selfQualified': True}})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']

    test_not_found = snitch(not_found)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_create_tender_bidder_document_json = snitch(create_tender_bidder_document_json)
    test_put_tender_bidder_document_json = snitch(put_tender_bidder_document_json)


class TenderBidderBatchDocumentsWithDSResourceTest(BaseTenderUAContentWebTest):
    docservice = True
    initial_status = 'active.tendering'

    bid_data_wo_docs = {'tenderers': [test_organization],
                        'value': {'amount': 500},
                        'selfEligible': True,
                        'selfQualified': True,
                        'documents': []
        }

    create_tender_bid_with_document_invalid = snitch(create_tender_bid_with_document_invalid)
    create_tender_bid_with_document = snitch(create_tender_bid_with_document)
    create_tender_bid_with_documents = snitch(create_tender_bid_with_documents)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
