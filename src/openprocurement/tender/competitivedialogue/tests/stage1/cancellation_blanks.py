# -*- coding: utf-8 -*-
from copy import deepcopy

from openprocurement.tender.belowthreshold.tests.base import test_cancellation
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_with_complaints_after_2020_04_19,
)


def cancellation_active_qualification_j1427(self):
    bid = deepcopy(self.initial_bids[0])
    bid["lotValues"] = bid["lotValues"][:1]

    # post three bids
    bid["tenderers"][0]["identifier"]["id"] = u"00037256"
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid})
    self.assertEqual(response.status, "201 Created")
    self.initial_bids_tokens[response.json["data"]["id"]] = response.json["access"]["token"]
    self.initial_bids.append(response.json["data"])
    bid_ids = [response.json["data"]["id"]]

    bid["tenderers"][0]["identifier"]["id"] = u"00037257"
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid})
    self.assertEqual(response.status, "201 Created")
    self.initial_bids_tokens[response.json["data"]["id"]] = response.json["access"]["token"]
    self.initial_bids.append(response.json["data"])
    bid_ids.append(response.json["data"]["id"])

    bid["tenderers"][0]["identifier"]["id"] = u"00037259"
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
