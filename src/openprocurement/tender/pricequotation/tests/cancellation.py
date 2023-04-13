import unittest
from unittest.mock import patch
from datetime import timedelta
from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch

from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_tender_pq_bids,
    test_tender_pq_cancellation,
)
from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationDocumentResourceTestMixin,
)
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


@patch("openprocurement.tender.pricequotation.models.requirement.PQ_CRITERIA_ID_FROM", get_now() + timedelta(days=1))
class TenderCancellationActiveTenderingResourceTest(
    TenderContentWebTest,
    TenderCancellationResourceTestMixin,
):
    initial_status = "active.tendering"
    initial_bids = test_tender_pq_bids
    valid_reasonType_choices = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]

    @property
    def tender_token(self):
        data = self.mongodb.tenders.get(self.tender_id)
        return data['owner_token']


class TenderCancellationActiveQualificationResourceTest(TenderCancellationActiveTenderingResourceTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_pq_bids
    valid_reasonType_choices = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]


class TenderCancellationActiveAwardedResourceTest(TenderCancellationActiveTenderingResourceTest):
    initial_status = "active.awarded"
    initial_bids = test_tender_pq_bids
    valid_reasonType_choices = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]


class TenderCancellationDocumentResourceTest(TenderContentWebTest, TenderCancellationDocumentResourceTestMixin):
    initial_status = "active.tendering"

    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        cancellation = dict(**test_tender_pq_cancellation)
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
