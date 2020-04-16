# -*- coding: utf-8 -*-
import unittest
from mock import patch
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_cancellation,
    test_organization,
)

from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    # TenderNegotiationLotsCancellationResourceTest
    patch_tender_lots_cancellation,
    # TenderCancellationResourceTest
    get_tender_cancellation,
    get_tender_cancellations,
    patch_tender_cancellation_2020_04_19,
    permission_cancellation_pending,
)
from openprocurement.tender.openua.tests.cancellation import (
    TenderCancellationResourceNewReleaseTestMixin,
    TenderCancellationComplaintResourceTestMixin,
)

from openprocurement.tender.openua.tests.cancellation_blanks import (
    # TenderCancellationResourceTest
    patch_tender_cancellation,
    activate_cancellation,
)

from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_lots,
    test_tender_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
)
from openprocurement.tender.limited.tests.cancellation_blanks import (
    # TenderNegotiationLotsCancellationResourceTest
    create_tender_lots_cancellation,
    cancelled_lot_without_relatedLot,
    delete_first_lot_second_cancel,
    cancel_tender,
    create_cancellation_on_tender_with_one_complete_lot,
    cancellation_on_not_active_lot,
    # TenderNegotiationCancellationResourceTest
    negotiation_create_cancellation_on_lot,
    # TenderCancellationResourceTest
    create_tender_cancellation_invalid,
    create_tender_cancellation,
    create_tender_cancellation_with_post,
    create_cancellation_on_lot,
)


class TenderCancellationResourceTestMixin(object):
    test_create_tender_cancellation_invalid = snitch(create_tender_cancellation_invalid)
    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_create_tender_cancellation_with_post = snitch(create_tender_cancellation_with_post)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_get_tender_cancellation = snitch(get_tender_cancellation)
    test_get_tender_cancellations = snitch(get_tender_cancellations)
    test_create_cancellation_on_lot = snitch(create_cancellation_on_lot)


class TenderCancellationResourceTest(
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
    BaseTenderContentWebTest,
):
    initial_data = test_tender_data

    test_patch_tender_cancellation_2020_04_19 = snitch(patch_tender_cancellation_2020_04_19)
    test_permission_cancellation_pending = snitch(permission_cancellation_pending)


@patch("openprocurement.tender.limited.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
class TenderNegotiationCancellationResourceTest(
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
    BaseTenderContentWebTest,
):
    def setUp(self):
        super(TenderNegotiationCancellationResourceTest, self).setUp()
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"suppliers": [test_organization], "qualified": True, "status": "active"}}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}}
        )
        self.set_all_awards_complaint_period_end()

    initial_data = test_tender_negotiation_data
    valid_reasonType_choices = ["noObjectiveness", "unFixable", "noDemand", "expensesCut", "dateViolation"]

    test_create_cancellation_on_lot = snitch(negotiation_create_cancellation_on_lot)
    test_activate_cancellation = snitch(activate_cancellation)


class TenderNegotiationQuickCancellationResourceTest(
    TenderNegotiationCancellationResourceTest,
    TenderCancellationResourceNewReleaseTestMixin
):
    def setUp(self):
        super(TenderNegotiationCancellationResourceTest, self).setUp()
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"suppliers": [test_organization], "qualified": True, "status": "active"}}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}}
        )
        self.set_all_awards_complaint_period_end()

    initial_data = test_tender_negotiation_quick_data
    valid_reasonType_choices = ["noObjectiveness", "unFixable", "noDemand", "expensesCut", "dateViolation"]


class TenderCancellationDocumentResourceTest(
    BaseTenderContentWebTest,
    TenderCancellationDocumentResourceTestMixin
):
    initial_data = test_tender_data

    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()

        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


class TenderNegotiationCancellationDocumentResourceTest(TenderCancellationDocumentResourceTest):
    initial_data = test_tender_negotiation_data


class TenderNegotiationQuickCancellationComplaintResourceTest(
    BaseTenderContentWebTest, TenderCancellationComplaintResourceTestMixin
):
    initial_data = test_tender_negotiation_quick_data

    @patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    def setUp(self):
        super(TenderNegotiationQuickCancellationComplaintResourceTest, self).setUp()
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"suppliers": [test_organization], "qualified": True, "status": "active"}}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}}
        )
        self.set_all_awards_complaint_period_end()

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


class TenderNegotiationCancellationComplaintResourceTest(
    BaseTenderContentWebTest, TenderCancellationComplaintResourceTestMixin
):
    initial_data = test_tender_negotiation_data

    @patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    def setUp(self):
        super(TenderNegotiationCancellationComplaintResourceTest, self).setUp()
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"suppliers": [test_organization], "qualified": True, "status": "active"}}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}}
        )
        self.set_all_awards_complaint_period_end()

        # create cancellation
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


class TenderNegotiationQuickCancellationDocumentResourceTest(TenderNegotiationCancellationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderNegotiationLotsCancellationResourceTest(BaseTenderContentWebTest):
    initial_lots = 2 * test_lots
    initial_data = test_tender_negotiation_data

    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)
    test_cancelled_lot_without_relatedLot = snitch(cancelled_lot_without_relatedLot)
    test_delete_first_lot_second_cancel = snitch(delete_first_lot_second_cancel)
    test_cancel_tender = snitch(cancel_tender)
    test_create_cancellation_on_tender_with_one_complete_lot = snitch(
        create_cancellation_on_tender_with_one_complete_lot
    )
    test_cancellation_on_not_active_lot = snitch(cancellation_on_not_active_lot)


class TenderNegotiationQuickLotsCancellationResourceTest(TenderNegotiationLotsCancellationResourceTest):
    initial_data = test_tender_negotiation_quick_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
