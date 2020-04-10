# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta
from mock import patch

from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_with_complaints_after_2020_04_19,
    skip_complaint_period_2020_04_19,
)

# TenderCancellationBidsAvailabilityTest
from openprocurement.tender.belowthreshold.tests.base import test_cancellation


@skip_complaint_period_2020_04_19
def bids_on_tender_cancellation_in_tendering(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertNotIn("bids", tender)  # bids not visible for others

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
    self.assertNotIn("bids", tender)
    self.assertEqual(tender["status"], "cancelled")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")


def bids_on_tender_cancellation_in_pre_qualification(self):
    self._mark_one_bid_deleted()

    # leave one bid invalidated
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"description": "2 b | !2 b"}}
    )
    for bid_id in self.valid_bids:
        response = self.app.get(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, self.initial_bids_tokens[bid_id])
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")
    invalid_bid_id = self.valid_bids.pop()
    self.assertEqual(len(self.valid_bids), (self.min_bids_number - 1) * 2)
    for bid_id in self.valid_bids:
        response = self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, self.initial_bids_tokens[bid_id]),
            {"data": {"status": "pending"}},
        )

    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    tender = self._cancel_tender()

    for bid in tender["bids"]:
        if bid["id"] in self.valid_bids:
            self.assertEqual(bid["status"], "invalid.pre-qualification")
            self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
        elif bid["id"] == invalid_bid_id:
            self.assertEqual(bid["status"], "invalid")
            self.assertEqual(set(bid.keys()), set(["id", "status"]))
        else:
            self.assertEqual(bid["status"], "deleted")
            self.assertEqual(set(bid.keys()), set(["id", "status"]))

    self._check_visible_fields_for_invalidated_bids()


@skip_complaint_period_2020_04_19
def bids_on_tender_cancellation_in_pre_qualification_stand_still(self):
    self._mark_one_bid_deleted()

    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    self._qualify_bids_and_switch_to_pre_qualification_stand_still()
    if RELEASE_2020_04_19 > get_now():
        # Test for old rules
        # In new rules there will be 403 error
        tender = self._cancel_tender()

        self.app.authorization = ("Basic", ("broker", ""))

        for bid in tender["bids"]:
            if bid["id"] in self.valid_bids:
                self.assertEqual(bid["status"], "invalid.pre-qualification")
                self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
            else:
                self.assertEqual(bid["status"], "deleted")
                self.assertEqual(set(bid.keys()), set(["id", "status"]))

        self._check_visible_fields_for_invalidated_bids()


def bids_on_tender_cancellation_in_auction(self):
    self._mark_one_bid_deleted()

    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    self._qualify_bids_and_switch_to_pre_qualification_stand_still()

    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    if RELEASE_2020_04_19 > get_now():

        tender = self._cancel_tender()

        self.app.authorization = ("Basic", ("broker", ""))
        for bid in tender["bids"]:
            if bid["id"] in self.valid_bids:
                self.assertEqual(bid["status"], "invalid.pre-qualification")
                self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
            else:
                self.assertEqual(bid["status"], "deleted")
                self.assertEqual(set(bid.keys()), set(["id", "status"]))
                self._all_documents_are_not_accessible(bid["id"])
        self._check_visible_fields_for_invalidated_bids()


def bids_on_tender_cancellation_in_qualification(self):
    self.bid_visible_fields = [
        u"status",
        u"documents",
        u"tenderers",
        u"id",
        u"selfQualified",
        u"eligibilityDocuments",
        u"selfEligible",
        u"value",
        u"date",
        u"financialDocuments",
        u"participationUrl",
        u"qualificationDocuments",
    ]
    deleted_bid_id = self._mark_one_bid_deleted()

    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    self._qualify_bids_and_switch_to_pre_qualification_stand_still(qualify_all=False)

    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self._set_auction_results()

    tender = self._cancel_tender()

    self.app.authorization = ("Basic", ("broker", ""))
    for bid in tender["bids"]:
        if bid["id"] in self.valid_bids:
            self.assertEqual(bid["status"], "active")
            self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
        elif bid["id"] == deleted_bid_id:
            self.assertEqual(bid["status"], "deleted")
            self.assertEqual(set(bid.keys()), set(["id", "status"]))
        else:
            self.assertEqual(bid["status"], "unsuccessful")
            self.assertEqual(
                set(bid.keys()),
                set(
                    [
                        u"documents",
                        u"eligibilityDocuments",
                        u"id",
                        u"status",
                        u"selfEligible",
                        u"tenderers",
                        u"selfQualified",
                    ]
                ),
            )

    for bid_id, bid_token in self.initial_bids_tokens.items():
        response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_id))
        bid_data = response.json["data"]

        if bid_id in self.valid_bids:
            self.assertEqual(set(bid_data.keys()), set(self.bid_visible_fields))

            for doc_resource in [
                "documents",
                "eligibility_documents",
                "financial_documents",
                "qualification_documents",
            ]:
                self._bid_document_is_accessible(bid_id, doc_resource)
        elif bid_id == deleted_bid_id:
            self._all_documents_are_not_accessible(bid_id)
        else:  # unsuccessful bid
            for doc_resource in ["financial_documents", "qualification_documents"]:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}".format(self.tender_id, bid_id, doc_resource), status=403
                )
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
            for doc_resource in ["documents", "eligibility_documents"]:
                self._bid_document_is_accessible(bid_id, doc_resource)


@skip_complaint_period_2020_04_19
def bids_on_tender_cancellation_in_awarded(self):
    self.bid_visible_fields = [
        u"status",
        u"documents",
        u"tenderers",
        u"id",
        u"selfQualified",
        u"eligibilityDocuments",
        u"selfEligible",
        u"value",
        u"date",
        u"financialDocuments",
        u"participationUrl",
        u"qualificationDocuments",
    ]
    self._mark_one_bid_deleted()

    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    self._qualify_bids_and_switch_to_pre_qualification_stand_still()

    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self._set_auction_results()

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    if RELEASE_2020_04_19 < get_now():
        self.set_all_awards_complaint_period_end()

    tender = self._cancel_tender()

    self.app.authorization = ("Basic", ("broker", ""))
    for bid in tender["bids"]:
        if bid["id"] in self.valid_bids:
            self.assertEqual(bid["status"], "active")
            self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
        else:
            self.assertEqual(bid["status"], "deleted")
            self.assertEqual(set(bid.keys()), set(["id", "status"]))

    for bid_id, bid_token in self.initial_bids_tokens.items():

        response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_id))
        bid_data = response.json["data"]
        if bid_id in self.valid_bids:
            self.assertEqual(set(bid_data.keys()), set(self.bid_visible_fields))

            for doc_resource in [
                "documents",
                "eligibility_documents",
                "financial_documents",
                "qualification_documents",
            ]:
                self._bid_document_is_accessible(bid_id, doc_resource)


# TenderAwardsCancellationResourceTest


@skip_complaint_period_2020_04_19
def cancellation_active_tendering_j708(self):
    bid = deepcopy(self.initial_bids[0])
    bid["lotValues"] = bid["lotValues"][:1]
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid})
    self.assertEqual(response.status, "201 Created")
    self.initial_bids_tokens[response.json["data"]["id"]] = response.json["access"]["token"]
    self.initial_bids.append(response.json["data"])

    response = self.app.delete(
        "/tenders/{}/bids/{}?acc_token={}".format(
            self.tender_id, response.json["data"]["id"], response.json["access"]["token"]
        )
    )
    self.assertEqual(response.status, "200 OK")

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "pending",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 > get_now():
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(
                self.tender_id, response.json["data"]["id"], self.tender_token
            ),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
    else:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)

    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid})
    self.assertEqual(response.status, "201 Created")
    self.initial_bids_tokens[response.json["data"]["id"]] = response.json["access"]["token"]
    self.initial_bids.append(response.json["data"])

    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")


def cancellation_active_qualification_j1427(self):
    bid = deepcopy(self.initial_bids[0])
    bid["lotValues"] = bid["lotValues"][:1]

    # post three bids
    bid_ids = []
    for i in range(3):
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid})
        self.assertEqual(response.status, "201 Created")
        self.initial_bids_tokens[response.json["data"]["id"]] = response.json["access"]["token"]
        self.initial_bids.append(response.json["data"])
        bid_ids.append(response.json["data"]["id"])

    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    qualification_id = [i["id"] for i in response.json["data"] if i["bidID"] == bid_ids[0]][0]
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )

    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    qualification_id = [i["id"] for i in response.json["data"] if i["bidID"] == bid_ids[1]][0]
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_ids[0]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_ids[1]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "invalid.pre-qualification")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_ids[2]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "invalid.pre-qualification")


def cancellation_active_qualification(self):
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    qualification_id = [
        i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == self.initial_lots[0]["id"]
    ][0]
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(cancellation["status"], "active")
    else:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation["id"])

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    if get_now() < RELEASE_2020_04_19:
        self.assertEqual(cancellation["status"], "active")
        self.assertIn("id", cancellation)
        self.assertIn(cancellation["id"], response.headers["Location"])
    else:
        self.assertEqual(cancellation["status"], "draft")
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)


def cancellation_unsuccessful_qualification(self):
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    self.app.authorization = ("Basic", ("token", ""))
    for i in range(self.min_bids_number):
        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        qualification_id = [
            i["id"]
            for i in response.json["data"]
            if i["status"] == "pending" and i["lotID"] == self.initial_lots[0]["id"]
        ][0]
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification_id, self.tender_token),
            {"data": {"status": "unsuccessful", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation if all qualifications are unsuccessful"
    )

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation if all qualifications are unsuccessful"
    )

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[1]["id"],
    })

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])
    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(cancellation["status"], "active")
    else:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation["id"])


@skip_complaint_period_2020_04_19
def cancellation_active_award(self):
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.app.authorization = ("Basic", ("token", ""))
    for qualification in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for lot_id in self.initial_lots:
        response = self.app.post_json(
            "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]), {"data": {"bids": auction_bids_data}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [
        i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == self.initial_lots[0]["id"]
    ][0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    if RELEASE_2020_04_19 < get_now():
        self.set_all_awards_complaint_period_end()

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(cancellation["status"], "active")
    else:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation["id"])

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    if get_now() < RELEASE_2020_04_19:
        self.assertEqual(cancellation["status"], "active")
        self.assertIn("id", cancellation)
        self.assertIn(cancellation["id"], response.headers["Location"])
    else:
        self.assertEqual(cancellation["status"], "draft")
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)


@skip_complaint_period_2020_04_19
def cancellation_unsuccessful_award(self):
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.app.authorization = ("Basic", ("token", ""))
    for qualification in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for lot_id in self.initial_lots:
        response = self.app.post_json(
            "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]), {"data": {"bids": auction_bids_data}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("token", ""))

    # patch all first lot related Awards to unsuccessful
    while True:
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        awards = [
            i["id"]
            for i in response.json["data"]
            if i["status"] == "pending" and i["lotID"] == self.initial_lots[0]["id"]
        ]
        if awards:
            award_id = awards[0]
        else:
            break
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
            {"data": {"status": "unsuccessful"}},
        )
        self.assertEqual(response.status, "200 OK")

    if RELEASE_2020_04_19 < get_now():
        self.set_all_awards_complaint_period_end()

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't perform cancellation if all awards are unsuccessful")

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't perform cancellation if all awards are unsuccessful")

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[1]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(cancellation["status"], "active")
    else:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation["id"])


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19",
            get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19",
            get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19",
            get_now() - timedelta(days=1))
def create_cancellation_in_qualification_complaint_period(self):
    self.set_status("active.qualification.stand-still")

    cancellation = dict(**test_cancellation)
    cancellation.update({"reasonType": "noDemand"})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u"description": u"Cancellation can't be add when exists active complaint period",
            u"location": u"body",
            u"name": u"data"
        }],
    )
