# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest, test_bids,
    test_cancellation,
)
from openprocurement.tender.belowthreshold.tests.cancellation import\
    TenderCancellationDocumentResourceTestMixin
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    get_tender_cancellation,
    get_tender_cancellations,
    )
from openprocurement.tender.pricequotation.tests.cancellation_blanks import (
    create_tender_cancellation,
    create_tender_cancellation_invalid,
    patch_tender_cancellation,
)


class TenderCancellationResourceTestMixin(object):
    initial_status = 'active.tendering'

    test_create_tender_cancellation_invalid = snitch(create_tender_cancellation_invalid)
    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_get_tender_cancellation = snitch(get_tender_cancellation)
    test_get_tender_cancellations = snitch(get_tender_cancellations)




class TenderCancellationActiveTenderingResourceTest(
    TenderContentWebTest,
    TenderCancellationResourceTestMixin,
):
    initial_status = "active.tendering"
    initial_bids = test_bids
    valid_reasonType_choices = ["noDemand", "unFixable", "expensesCut"]

    @property
    def tender_token(self):
        data = self.db.get(self.tender_id)
        return data['owner_token']


class TenderCancellationActiveQualificationResourceTest(TenderCancellationActiveTenderingResourceTest):
    initial_status = "active.qualification"
    initial_bids = test_bids
    valid_reasonType_choices = ["noDemand", "unFixable", "expensesCut"]


class TenderCancellationActiveAwardedResourceTest(TenderCancellationActiveTenderingResourceTest):
    initial_status = "active.awarded"
    initial_bids = test_bids
    valid_reasonType_choices = ["noDemand", "unFixable", "expensesCut"]


class TenderCancellationDocumentResourceTest(TenderContentWebTest, TenderCancellationDocumentResourceTestMixin):
    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        cancellation = dict(**test_cancellation)
        cancellation.update({
            "reasonType": "noDemand"
        })

        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationActiveTenderingResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
