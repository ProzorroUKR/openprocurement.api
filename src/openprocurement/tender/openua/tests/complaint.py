import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_draft_complaint,
    test_tender_below_lots,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (  # TenderComplaintDocumentResourceTest
    create_tender_complaint_document,
    not_found,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.open.tests.complaint import (
    ComplaintObjectionMixin,
    TenderAwardComplaintObjectionMixin,
    TenderCancellationComplaintObjectionMixin,
    TenderComplaintObjectionMixin,
)
from openprocurement.tender.openua.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openua_bids,
)
from openprocurement.tender.openua.tests.complaint_blanks import (  # TenderComplaintResourceTest; TenderComplaintDocumentResourceTest; TenderLotAwardComplaintResourceTest
    bot_patch_tender_complaint,
    bot_patch_tender_complaint_forbidden,
    bot_patch_tender_complaint_mistaken,
    create_tender_complaint,
    mistaken_status_tender_complaint,
    patch_tender_complaint,
    patch_tender_complaint_document,
    put_tender_complaint_document,
    review_tender_complaint,
    review_tender_stopping_complaint,
)


class TenderUAComplaintResourceTestMixin:
    test_create_tender_complaint = snitch(create_tender_complaint)
    test_patch_tender_complaint = snitch(patch_tender_complaint)
    test_review_tender_complaint = snitch(review_tender_complaint)
    test_review_tender_stopping_complaint = snitch(review_tender_stopping_complaint)
    test_mistaken_status_tender_complaint = snitch(mistaken_status_tender_complaint)
    test_bot_patch_tender_complaint = snitch(bot_patch_tender_complaint)
    test_bot_patch_tender_complaint_mistaken = snitch(bot_patch_tender_complaint_mistaken)
    test_bot_patch_tender_complaint_forbidden = snitch(bot_patch_tender_complaint_forbidden)


class TenderComplaintResourceTest(BaseTenderUAContentWebTest, TenderUAComplaintResourceTestMixin):
    test_author = test_tender_below_author


class TenderComplaintDocumentResourceTest(BaseTenderUAContentWebTest):
    def setUp(self):
        super().setUp()
        # Create complaint
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_not_found = snitch(not_found)
    test_create_tender_complaint_document = snitch(create_tender_complaint_document)
    test_put_tender_complaint_document = snitch(put_tender_complaint_document)
    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document)


class CreateAwardComplaintMixin:
    app = None
    tender_id = None
    initial_bids = None
    initial_bids_tokens = None

    def create_award(self):
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                f"/tenders/{self.tender_id}/awards",
                {
                    "data": {
                        "suppliers": [test_tender_below_organization],
                        "status": "pending",
                        "bid_id": self.initial_bids[0]["id"],
                        "lotID": self.initial_lots[0]["id"],
                    }
                },
            )

        award = response.json["data"]
        self.award_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")

        with change_auth(self.app, ("Basic", ("token", ""))):
            patch_data = {"status": "active", "qualified": True}
            if self.initial_data['procurementMethodType'] != "simple.defense":
                patch_data["eligible"] = True
            self.app.patch_json(
                f"/tenders/{self.tender_id}/awards/{self.award_id}",
                {"data": patch_data},
            )


class TenderComplaintObjectionResourceTest(
    BaseTenderUAContentWebTest,
    TenderComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    pass


class TenderAwardComplaintObjectionResourceTest(
    BaseTenderUAContentWebTest,
    CreateAwardComplaintMixin,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    initial_status = "active.qualification"
    initial_bids = test_tender_openua_bids
    initial_lots = test_tender_below_lots

    def setUp(self):
        super().setUp()
        self.create_award()


class TenderCancellationComplaintObjectionResourceTest(
    BaseTenderUAContentWebTest,
    TenderCancellationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):

    def setUp(self):
        super().setUp()
        self.create_cancellation()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintObjectionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintObjectionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationComplaintObjectionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
