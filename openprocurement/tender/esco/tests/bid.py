# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.esco.tests.base import (
    test_bids, test_features_tender_data,
    BaseESCOEUContentWebTest
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_organization,
)
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderBidBatchDocumentWithDSResourceTest
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
)
from openprocurement.tender.openeu.tests.bid import TenderBidDocumentResourceTestMixin
from openprocurement.tender.openeu.tests.bid_blanks import (
    # TenderBidDocumentWithDSResourceTest
    patch_tender_bidder_document_private_json,
    put_tender_bidder_document_private_json,
    get_tender_bidder_document_ds,
    # TenderBidDocumentResourceTest
    patch_tender_bidder_document_private,
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
    patch_and_put_document_into_invalid_bid
)


class TenderBidResourceTest(BaseESCOEUContentWebTest):
    initial_status = 'active.tendering'
    test_bids_data = test_bids # TODO: change attribute identificator
    author_data = test_bids_data[0]['tenderers'][0]

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_create_tender_bid = snitch(create_tender_bid)
    test_patch_tender_bid = snitch(patch_tender_bid)

    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)


class TenderBidFeaturesResourceTest(BaseESCOEUContentWebTest):
    initial_status = 'active.tendering'
    initial_data = test_features_tender_data
    test_bids_data = test_bids # TODO: change attribute identificator

    test_features_bid = snitch(features_bid)
    test_features_bid_invalid = snitch(features_bid_invalid)


class TenderBidDocumentResourceTest(BaseESCOEUContentWebTest, TenderBidDocumentResourceTestMixin):
    initial_auth = ('Basic', ('broker', ''))
    initial_status = 'active.tendering'
    test_bids_data = test_bids

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': test_bids[0]})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']
        # create second bid
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': test_bids[1]})
        bid2 = response.json['data']
        self.bid2_id = bid2['id']
        self.bid2_token = response.json['access']['token']

    test_patch_and_put_document_into_invalid_bid = snitch(patch_and_put_document_into_invalid_bid)
    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_patch_tender_bidder_document_private_json = snitch(patch_tender_bidder_document_private_json)
    test_put_tender_bidder_document_private_json = snitch(put_tender_bidder_document_private_json)
    test_get_tender_bidder_document_ds = snitch(get_tender_bidder_document_ds)



class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True


class TenderBidBatchDocumentsWithDSResourceTest(BaseESCOEUContentWebTest):
    docservice = True
    initial_status = 'active.tendering'


    bid_data_wo_docs = {'tenderers': [test_organization],
                        'value': test_bids[0]['value'],
                        'selfEligible': True,
                        'selfQualified': True,
                        'documents': []
        }

    test_create_tender_bid_with_document_invalid = snitch(create_tender_bid_with_document_invalid)
    test_create_tender_bid_with_document = snitch(create_tender_bid_with_document)
    test_create_tender_bid_with_documents = snitch(create_tender_bid_with_documents)

    test_create_tender_bid_with_eligibility_document_invalid = snitch(create_tender_bid_with_eligibility_document_invalid)
    test_create_tender_bid_with_eligibility_document = snitch(create_tender_bid_with_eligibility_document)
    test_create_tender_bid_with_eligibility_documents = snitch(create_tender_bid_with_eligibility_documents)

    test_create_tender_bid_with_qualification_document_invalid = snitch(create_tender_bid_with_qualification_document_invalid)
    test_create_tender_bid_with_qualification_document = snitch(create_tender_bid_with_qualification_document)
    test_create_tender_bid_with_qualification_documents = snitch(create_tender_bid_with_qualification_documents)

    test_create_tender_bid_with_financial_document_invalid = snitch(create_tender_bid_with_financial_document_invalid)
    test_create_tender_bid_with_financial_document = snitch(create_tender_bid_with_financial_document)
    test_create_tender_bid_with_financial_documents = snitch(create_tender_bid_with_financial_documents)

    test_create_tender_bid_with_all_documents = snitch(create_tender_bid_with_all_documents)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TenderBidResourceTest)
    suite.addTest(TenderBidFeaturesResourceTest)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
