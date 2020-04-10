# -*- coding: utf-8 -*-
import unittest
from mock import patch
from datetime import timedelta

from openprocurement.api.utils import get_now

from openprocurement.api.tests.base import snitch
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.belowthreshold.tests.base import test_cancellation
from openprocurement.tender.core.tests.cancellation import activate_cancellation_with_complaints_after_2020_04_19

from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationResourceTestMixin,
    TenderCancellationDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    # TenderLotsCancellationResourceTest
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
    # TenderLotCancellationResourceTest
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
)
from openprocurement.tender.openua.tests.cancellation import (
    TenderCancellationResourceNewReleaseTestMixin,
    TenderCancellationComplaintResourceTestMixin,
)

from openprocurement.tender.openua.tests.cancellation_blanks import (
    # TenderCancellationResourceTest
    create_tender_cancellation,
    patch_tender_cancellation,
    access_create_tender_cancellation_complaint,
    activate_cancellation,
    create_cancellation_in_tender_complaint_period,
    create_cancellation_in_award_complaint_period,
    create_tender_cancellation_with_cancellation_lots,
)

from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest, test_bids, test_lots
from openprocurement.tender.openeu.tests.cancellation_blanks import (
    # TenderAwardsCancellationResourceTest
    cancellation_active_tendering_j708,
    cancellation_active_qualification_j1427,
    cancellation_active_qualification,
    cancellation_unsuccessful_qualification,
    cancellation_active_award,
    cancellation_unsuccessful_award,
    # TenderCancellationBidsAvailabilityTest
    bids_on_tender_cancellation_in_tendering,
    bids_on_tender_cancellation_in_pre_qualification,
    bids_on_tender_cancellation_in_pre_qualification_stand_still,
    bids_on_tender_cancellation_in_auction,
    bids_on_tender_cancellation_in_qualification,
    bids_on_tender_cancellation_in_awarded,
    create_cancellation_in_qualification_complaint_period,
)


class TenderCancellationBidsAvailabilityUtils(object):
    def _mark_one_bid_deleted(self):
        bid_id, bid_token = self.initial_bids_tokens.items()[0]
        response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token))
        self.assertEqual(response.status, "200 OK")
        self.valid_bids.remove(bid_id)
        return bid_id

    def _prepare_bids_docs(self):
        doc_id_by_type = {}
        for bid_id, bid_token in self.initial_bids_tokens.items():
            for doc_resource in [
                "documents",
                "financial_documents",
                "eligibility_documents",
                "qualification_documents",
            ]:
                response = self.app.post(
                    "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, bid_id, doc_resource, bid_token),
                    upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
                )
                doc_id = response.json["data"]["id"]

                self.assertIn(doc_id, response.headers["Location"])
                self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
                key = response.json["data"]["url"].split("?")[-1]
                doc_id_by_type[bid_id + doc_resource] = {"id": doc_id, "key": key}

        self.doc_id_by_type = doc_id_by_type

    def _cancel_tender(self):
        orig_authorization = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        cancellation = dict(**test_cancellation)
        cancellation.update({
            "status": "active",
        })
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        self.assertEqual(response.status, "201 Created")
        cancellation = response.json["data"]
        cancellation_id = cancellation["id"]
        if get_now() < RELEASE_2020_04_19:
            self.assertEqual(cancellation["status"], "active")
        else:
            self.assertEqual(cancellation["status"], "draft")
            activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)

        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]
        self.assertIn("bids", tender)
        self.assertEqual(tender["status"], "cancelled")
        self.app.authorization = orig_authorization
        return tender

    def _qualify_bids_and_switch_to_pre_qualification_stand_still(self, qualify_all=True):
        orig_authorization = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        qualifications = response.json["data"]
        self.assertEqual(len(qualifications), self.min_bids_number * 2 - 1)
        offset = 0 if qualify_all else 1
        for qualification in qualifications[offset:]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        if offset:
            qualification = qualifications[0]
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "unsuccessful"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.valid_bids.remove(qualification["bidID"])

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")
        self.app.authorization = orig_authorization

    def _all_documents_are_not_accessible(self, bid_id):
        for doc_resource in ["documents", "eligibility_documents", "financial_documents", "qualification_documents"]:
            response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, bid_id, doc_resource), status=403)
            self.assertEqual(response.status, "403 Forbidden")
            self.assertIn("Can't view bid documents in current (", response.json["errors"][0]["description"])
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}".format(
                    self.tender_id, bid_id, doc_resource, self.doc_id_by_type[bid_id + doc_resource]["id"]
                ),
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertIn("Can't view bid documents in current (", response.json["errors"][0]["description"])

    def _check_visible_fields_for_invalidated_bids(self):
        orig_authorization = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))

        for bid_id, bid_token in self.initial_bids_tokens.items():
            response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_id))
            bid_data = response.json["data"]
            if bid_id in self.valid_bids:
                self.assertEqual(set(bid_data.keys()), set(self.bid_visible_fields))

                for doc_resource in ["documents", "eligibility_documents"]:
                    response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, bid_id, doc_resource))
                    docs = response.json["data"]
                    self.assertEqual(len(docs), 1)
                    self.assertEqual(docs[0]["title"], "name_{}.doc".format(doc_resource[:-1]))
                    self.assertIn("url", docs[0])

                for doc_resource in ["financial_documents", "qualification_documents"]:
                    response = self.app.get(
                        "/tenders/{}/bids/{}/{}".format(self.tender_id, bid_id, doc_resource), status=403
                    )
                    self.assertEqual(response.status, "403 Forbidden")
                    self.assertEqual(
                        response.json["errors"][0]["description"],
                        "Can't view bid documents in current (invalid.pre-qualification) bid status",
                    )
                    response = self.app.get(
                        "/tenders/{}/bids/{}/{}/{}".format(
                            self.tender_id, bid_id, doc_resource, self.doc_id_by_type[bid_id + doc_resource]["id"]
                        ),
                        status=403,
                    )
                    self.assertEqual(response.status, "403 Forbidden")
                    self.assertEqual(
                        response.json["errors"][0]["description"],
                        "Can't view bid documents in current (invalid.pre-qualification) bid status",
                    )
            else:
                self.assertEqual(set(bid_data.keys()), set(["id", "status"]))
                self._all_documents_are_not_accessible(bid_id)

        self.app.authorization = orig_authorization

    def _set_auction_results(self):
        orig_authorization = self.app.authorization
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        response = self.app.patch_json(
            "/tenders/{}/auction".format(self.tender_id),
            {
                "data": {
                    "auctionUrl": "https://tender.auction.url",
                    "bids": [
                        {"id": i["id"], "participationUrl": "https://tender.auction.url/for_bid/{}".format(i["id"])}
                        for i in auction_bids_data
                    ],
                }
            },
        )
        response = self.app.post_json(
            "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": auction_bids_data}}
        )
        self.assertEqual(response.status, "200 OK")
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "active.qualification")
        self.app.authorization = orig_authorization

    def _bid_document_is_accessible(self, bid_id, doc_resource):
        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, bid_id, doc_resource))
        docs = response.json["data"]
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]["title"], "name_{}.doc".format(doc_resource[:-1]))
        self.assertIn("url", docs[0])
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(
                self.tender_id, bid_id, doc_resource, self.doc_id_by_type[bid_id + doc_resource]["id"]
            )
        )
        doc = response.json["data"]
        self.assertEqual(doc["title"], "name_{}.doc".format(doc_resource[:-1]))


class TenderCancellationResourceTest(
    BaseTenderContentWebTest,
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin
):
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_activate_cancellation = snitch(activate_cancellation)
    test_create_cancellation_in_tender_complaint_period = snitch(create_cancellation_in_tender_complaint_period)


class TenderCancellationBidsAvailabilityTest(
    BaseTenderContentWebTest,
    TenderCancellationBidsAvailabilityUtils
):
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = test_bids * 2
    bid_visible_fields = [u"status", u"documents", u"tenderers", u"id", u"eligibilityDocuments"]
    doc_id_by_type = {}
    valid_bids = []

    def setUp(self):
        super(TenderCancellationBidsAvailabilityTest, self).setUp()
        self.valid_bids = self.initial_bids_tokens.keys()
        self._prepare_bids_docs()

    test_bids_on_tender_cancellation_in_tendering = snitch(bids_on_tender_cancellation_in_tendering)
    test_bids_on_tender_cancellation_in_pre_qualification = snitch(bids_on_tender_cancellation_in_pre_qualification)
    test_bids_on_tender_cancellation_in_pre_qualification_stand_still = snitch(
        bids_on_tender_cancellation_in_pre_qualification_stand_still
    )
    test_bids_on_tender_cancellation_in_auction = snitch(bids_on_tender_cancellation_in_auction)
    test_bids_on_tender_cancellation_in_qualification = snitch(bids_on_tender_cancellation_in_qualification)
    test_bids_on_tender_cancellation_in_awarded = snitch(bids_on_tender_cancellation_in_awarded)
    test_create_cancellation_in_qualification_complaint_period = snitch(create_cancellation_in_qualification_complaint_period)


class TenderLotCancellationResourceTest(BaseTenderContentWebTest):
    initial_lots = test_lots

    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseTenderContentWebTest):
    initial_lots = 2 * test_lots

    initial_auth = ("Basic", ("broker", ""))
    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_create_tender_cancellation_with_cancellation_lots = snitch(create_tender_cancellation_with_cancellation_lots)
    # test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)


class TenderAwardsCancellationResourceTest(BaseTenderContentWebTest):
    initial_lots = 2 * test_lots
    initial_status = "active.tendering"
    initial_bids = test_bids

    test_cancellation_active_tendering_j708 = snitch(cancellation_active_tendering_j708)
    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)
    test_cancellation_active_qualification = snitch(cancellation_active_qualification)
    test_cancellation_unsuccessful_qualification = snitch(cancellation_unsuccessful_qualification)
    test_cancellation_active_award = snitch(cancellation_active_award)
    test_cancellation_unsuccessful_award = snitch(cancellation_unsuccessful_award)
    test_create_cancellation_in_award_complaint_period = snitch(create_cancellation_in_award_complaint_period)


class TenderCancellationComplaintResourceTest(
    BaseTenderContentWebTest,
    TenderCancellationComplaintResourceTestMixin
):
    initial_bids = test_bids

    @patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    def setUp(self):
        super(TenderCancellationComplaintResourceTest, self).setUp()
        self.set_complaint_period_end()

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

    test_access_create_tender_cancellation_complaint = snitch(access_create_tender_cancellation_complaint)


class TenderCancellationDocumentResourceTest(
    BaseTenderContentWebTest,
    TenderCancellationDocumentResourceTestMixin
):
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()

        if RELEASE_2020_04_19 < get_now():
            self.set_complaint_period_end()

        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
