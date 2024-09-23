import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (  # TenderNegotiationLotsCancellationResourceTest; TenderCancellationResourceTest
    get_tender_cancellation,
    get_tender_cancellations,
    patch_tender_cancellation_2020_04_19,
    patch_tender_lots_cancellation,
    permission_cancellation_pending,
)
from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_lots,
    test_tender_negotiation_config,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_config,
    test_tender_negotiation_quick_data,
    test_tender_reporting_data,
)
from openprocurement.tender.limited.tests.cancellation_blanks import (  # TenderNegotiationLotsCancellationResourceTest; TenderNegotiationCancellationResourceTest; TenderCancellationResourceTest
    cancel_tender,
    cancellation_on_not_active_lot,
    cancelled_lot_without_relatedLot,
    create_cancellation_on_lot,
    create_cancellation_on_tender_with_one_complete_lot,
    create_tender_cancellation,
    create_tender_cancellation_invalid,
    create_tender_cancellation_with_post,
    create_tender_lots_cancellation,
    delete_first_lot_second_cancel,
    negotiation_create_cancellation_on_lot,
)
from openprocurement.tender.openua.tests.cancellation import (
    TenderCancellationComplaintResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
)
from openprocurement.tender.openua.tests.cancellation_blanks import (  # TenderCancellationResourceTest
    activate_cancellation,
    patch_tender_cancellation,
)


class TenderCancellationResourceTestMixin:
    test_create_tender_cancellation_invalid = snitch(create_tender_cancellation_invalid)
    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_create_tender_cancellation_with_post = snitch(create_tender_cancellation_with_post)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_get_tender_cancellation = snitch(get_tender_cancellation)
    test_get_tender_cancellations = snitch(get_tender_cancellations)
    test_create_cancellation_on_lot = snitch(create_cancellation_on_lot)
    test_create_cancellation_with_tender_complaint = None


class TenderCancellationResourceTest(
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
    BaseTenderContentWebTest,
):
    initial_data = test_tender_reporting_data

    test_patch_tender_cancellation_2020_04_19 = snitch(patch_tender_cancellation_2020_04_19)
    test_patch_tender_cancellation_2020_04_19_to_pending = None
    test_permission_cancellation_pending = snitch(permission_cancellation_pending)


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
class TenderNegotiationCancellationResourceTest(
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
    BaseTenderContentWebTest,
):
    initial_config = test_tender_negotiation_config

    def setUp(self):
        super().setUp()
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True}},
        )
        self.set_all_awards_complaint_period_end()

    initial_data = test_tender_negotiation_data
    valid_reasonType_choices = ["noObjectiveness", "unFixable", "noDemand", "expensesCut", "dateViolation"]

    test_create_cancellation_on_lot = snitch(negotiation_create_cancellation_on_lot)
    test_activate_cancellation = snitch(activate_cancellation)


class TenderNegotiationQuickCancellationResourceTest(
    TenderNegotiationCancellationResourceTest, TenderCancellationResourceNewReleaseTestMixin
):
    initial_config = test_tender_negotiation_quick_config

    def setUp(self):
        super(TenderNegotiationCancellationResourceTest, self).setUp()
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True}},
        )
        self.set_all_awards_complaint_period_end()

    initial_data = test_tender_negotiation_quick_data
    valid_reasonType_choices = ["noObjectiveness", "unFixable", "noDemand", "expensesCut", "dateViolation"]


class TenderCancellationDocumentResourceTest(BaseTenderContentWebTest, TenderCancellationDocumentResourceTestMixin):
    initial_data = test_tender_reporting_data

    def setUp(self):
        super().setUp()

        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_tender_below_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


class TenderNegotiationCancellationDocumentResourceTest(TenderCancellationDocumentResourceTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config


class TenderNegotiationQuickCancellationComplaintResourceTest(
    BaseTenderContentWebTest, TenderCancellationComplaintResourceTestMixin
):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config

    @patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    def setUp(self):
        super().setUp()
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True}},
        )
        self.set_all_awards_complaint_period_end()

        # Create cancellation
        cancellation = deepcopy(test_tender_below_cancellation)
        cancellation.update({"reasonType": "noDemand"})
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
    initial_config = test_tender_negotiation_config

    @patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    def setUp(self):
        super().setUp()
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True}},
        )
        self.set_all_awards_complaint_period_end()

        # create cancellation
        cancellation = deepcopy(test_tender_below_cancellation)
        cancellation.update({"reasonType": "noDemand"})
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


class TenderNegotiationQuickCancellationDocumentResourceTest(TenderNegotiationCancellationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config


class TenderNegotiationLotsCancellationResourceTest(BaseTenderContentWebTest):
    initial_lots = 2 * test_lots
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config

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
    initial_config = test_tender_negotiation_quick_config


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
