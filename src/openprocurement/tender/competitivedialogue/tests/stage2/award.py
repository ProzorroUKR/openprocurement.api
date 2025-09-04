import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.award import (
    Tender2LotAwardDocumentResourceTestMixin,
    TenderAwardComplaintDocumentResourceTestMixin,
    TenderAwardComplaintResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    create_tender_lots_award_complaint_document,
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_tender_cd_author,
    test_tender_cd_lots,
    test_tender_cd_tenderer,
    test_tender_openeu_bids,
)
from openprocurement.tender.competitivedialogue.tests.stage2.award_blanks import (
    create_tender_award_complaint_document,
    create_tender_award_invalid,
    get_tender_award,
    patch_tender_award_complaint_document,
    put_tender_award_complaint_document,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.openeu.tests.award import (
    Tender2LotAwardComplaintResourceTestMixin,
    Tender2LotAwardResourceTestMixin,
    TenderLotAwardComplaintResourceTestMixin,
    TenderLotAwardResourceTestMixin,
)
from openprocurement.tender.openua.tests.award import (
    TenderUAAwardComplaintResourceTestMixin,
)
from openprocurement.tender.openua.tests.award_blanks import (
    create_tender_lot_award,
    create_tender_lot_award_complaint,
    create_tender_lots_award,
    create_tender_lots_award_complaint,
    patch_tender_award_active,
)
from openprocurement.tender.openua.tests.award_blanks import (
    patch_tender_award_complaint_document as patch_tender_award_complaint_document_from_ua,
)
from openprocurement.tender.openua.tests.award_blanks import (
    patch_tender_lot_award,
    patch_tender_lot_award_complaint,
    patch_tender_lot_award_unsuccessful,
    patch_tender_lots_award,
    patch_tender_lots_award_complaint,
    patch_tender_lots_award_complaint_document,
    put_tender_lots_award_complaint_document,
)

test_tender_bids = deepcopy(test_tender_openeu_bids[:2])
for test_bid in test_tender_bids:
    test_bid["tenderers"] = [test_tender_cd_tenderer]


class TenderStage2EULotAwardResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderLotAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amount = test_tender_openeu_bids[0]["value"]["amount"]

    def setUp(self):
        super().setUp()
        # switch to active.pre-qualification
        self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        # qualify bids
        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.auction")

        with change_auth(self.app, ("Basic", ("auction", ""))):
            response = self.app.get("/tenders/{}/auction".format(self.tender_id))
            auction_bids_data = [
                {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                for b in response.json["data"]["bids"]
            ]
            for lot_id in self.lots:
                response = self.app.post_json(
                    "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]), {"data": {"bids": auction_bids_data}}
                )
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.content_type, "application/json")
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "active.qualification")

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.bid_token = self.initial_bids_tokens[self.bids[0]["id"]]


class TenderStage2EU2LotAwardResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, Tender2LotAwardResourceTestMixin
):
    initial_status = "active.tendering"
    initial_lots = deepcopy(2 * test_tender_cd_lots)
    initial_bids = test_tender_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
        # switch to active.pre-qualification
        self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        # qualify bids
        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.auction")

        with change_auth(self.app, ("Basic", ("auction", ""))):
            response = self.app.get("/tenders/{}/auction".format(self.tender_id))
            auction_bids_data = [
                {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                for b in response.json["data"]["bids"]
            ]
            for lot_id in self.lots:
                response = self.app.post_json(
                    "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]), {"data": {"bids": auction_bids_data}}
                )
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.content_type, "application/json")
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "active.qualification")

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]


class TenderStage2EUAwardComplaintResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest,
    TenderAwardComplaintResourceTestMixin,
    TenderUAAwardComplaintResourceTestMixin,
):
    initial_status = "active.tendering"
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_tender_cd_lots)
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
        # switch to active.pre-qualification
        self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        # qualify bids
        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        self.app.authorization = ("Basic", ("broker", ""))
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.auction")

        with change_auth(self.app, ("Basic", ("auction", ""))):
            response = self.app.get("/tenders/{}/auction".format(self.tender_id))
            auction_bids_data = [
                {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                for b in response.json["data"]["bids"]
            ]
            for lot_id in self.lots:
                response = self.app.post_json(
                    "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]), {"data": {"bids": auction_bids_data}}
                )
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.content_type, "application/json")
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "active.qualification")

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.bid_token = self.initial_bids_tokens[self.bids[0]["id"]]


class TenderStage2EULotAwardComplaintResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, TenderLotAwardComplaintResourceTestMixin
):
    initial_status = "active.tendering"
    initial_lots = deepcopy(test_tender_cd_lots)
    initial_bids = test_tender_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        # switch to active.pre-qualification
        self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        # qualify bids
        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.auction")

        with change_auth(self.app, ("Basic", ("auction", ""))):
            response = self.app.get("/tenders/{}/auction".format(self.tender_id))
            auction_bids_data = [
                {
                    "id": b["id"],
                    "lotValues": [{"relatedLot": l["relatedLot"], "value": l["value"]} for l in b["lotValues"]],
                }
                for b in response.json["data"]["bids"]
            ]
            for lot_id in self.lots:
                response = self.app.post_json(
                    "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]), {"data": {"bids": auction_bids_data}}
                )
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.content_type, "application/json")
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "active.qualification")

        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            bid = self.bids[0]
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_cd_tenderer],
                        "status": "pending",
                        "bid_id": bid["id"],
                        "lotID": bid["lotValues"][0]["relatedLot"],
                    }
                },
            )
            award = response.json["data"]
            self.award_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.bid_token = self.initial_bids_tokens[self.bids[0]["id"]]


class TenderStage2EU2LotAwardComplaintResourceTest(
    TenderStage2EULotAwardComplaintResourceTest, Tender2LotAwardComplaintResourceTestMixin
):
    initial_lots = deepcopy(2 * test_tender_cd_lots)


class TenderStage2EUAwardComplaintDocumentResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, TenderAwardComplaintDocumentResourceTestMixin
):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_cd_tenderer],
                        "status": "pending",
                        "bid_id": self.bids[0]["id"],
                        "lotID": self.initial_lots[0]["id"],
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        # Create complaint for award
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={list(self.initial_bids_tokens.values())[0]}",
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document_from_ua)


class TenderStage2EU2LotAwardComplaintDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_tender_cd_lots)

    def setUp(self):
        super().setUp()
        # Create award
        bid = self.bids[0]
        with change_auth(self.app, ("Basic", ("token", ""))):
            self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_cd_tenderer],
                        "status": "pending",
                        "bid_id": bid["id"],
                        "lotID": bid["lotValues"][1]["relatedLot"],
                    }
                },
            )
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_cd_tenderer],
                        "status": "pending",
                        "bid_id": bid["id"],
                        "lotID": bid["lotValues"][0]["relatedLot"],
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        # Create complaint for award
        claim_data = deepcopy(test_tender_below_draft_complaint)
        claim_data["author"] = test_tender_cd_author
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={list(self.initial_bids_tokens.values())[0]}",
            {"data": claim_data},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_create_tender_award_complaint_document = snitch(create_tender_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class TenderStage2EUAwardDocumentResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, TenderAwardDocumentResourceTestMixin
):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_cd_tenderer],
                        "status": "pending",
                        "bid_id": self.bids[0]["id"],
                        "lotID": self.initial_lots[0]["id"],
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]


class TenderStage2EU2LotAwardDocumentResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, Tender2LotAwardDocumentResourceTestMixin
):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_tender_cd_lots)

    def setUp(self):
        super().setUp()
        # Create award
        bid = self.bids[0]
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_cd_tenderer],
                        "status": "pending",
                        "bid_id": bid["id"],
                        "lotID": bid["lotValues"][0]["relatedLot"],
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]


# UA


class TenderStage2UAAwardResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots

    test_patch_tender_award_active = snitch(patch_tender_award_active)
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_get_tender_award = snitch(get_tender_award)


class TenderStage2UALotAwardResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.qualification"
    initial_lots = deepcopy(test_tender_cd_lots)
    initial_bids = test_tender_bids

    test_create_lot_award = snitch(create_tender_lot_award)
    test_patch_tender_lot_award = snitch(patch_tender_lot_award)
    test_patch_tender_lot_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)


class TenderStage2UA2LotAwardResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.qualification"
    initial_lots = deepcopy(2 * test_tender_cd_lots)
    initial_bids = test_tender_bids

    test_create_tender_lots_award = snitch(create_tender_lots_award)
    test_patch_tender_lots_award = snitch(patch_tender_lots_award)


class BaseTenderUAAwardPendingTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids

    def setUp(self):
        super().setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_cd_tenderer],
                        "status": "pending",
                        "bid_id": self.bids[0]["id"],
                        "lotID": self.initial_bids[0]["lotValues"][0]["relatedLot"] if self.initial_lots else None,
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]


class BaseTenderUAAwardActiveTest(BaseTenderUAAwardPendingTest):
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        with change_auth(self.app, ("Basic", ("token", ""))):
            self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
        self.bid_token = self.initial_bids_tokens[self.bids[0]["id"]]


class TenderStage2UAAwardComplaintResourceTest(
    BaseTenderUAAwardActiveTest,
    TenderAwardComplaintResourceTestMixin,
    TenderUAAwardComplaintResourceTestMixin,
):
    pass


class TenderStage2UALotAwardComplaintResourceTest(BaseTenderUAAwardActiveTest):
    initial_lots = deepcopy(test_tender_cd_lots)

    test_create_tender_lot_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_lot_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_lot_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_lot_award_complaints = snitch(get_tender_lot_award_complaints)


class Tender2LotAwardComplaintResourceTest(TenderStage2UALotAwardComplaintResourceTest):
    initial_lots = deepcopy(2 * test_tender_cd_lots)

    test_create_tender_lots_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_lots_award_complaint = snitch(patch_tender_lots_award_complaint)


class TenderStage2UAAwardComplaintDocumentResourceTest(
    BaseTenderUAAwardActiveTest, TenderAwardComplaintDocumentResourceTestMixin
):
    def setUp(self):
        super().setUp()

        # Create complaint for award
        bid_token = self.initial_bids_tokens[self.bids[0]["id"]]
        claim_data = deepcopy(test_tender_below_draft_complaint)
        claim_data["author"] = test_tender_cd_author
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
            {"data": claim_data},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class TenderStage2UA2LotAwardComplaintDocumentResourceTest(BaseTenderUAAwardActiveTest):
    initial_lots = deepcopy(2 * test_tender_cd_lots)

    def setUp(self):
        super().setUp()

        # Create complaint for award
        claim_data = deepcopy(test_tender_below_draft_complaint)
        claim_data["author"] = test_tender_cd_author
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
            {"data": claim_data},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_create_tender_lots_award_document = snitch(create_tender_lots_award_complaint_document)
    test_put_tender_lots_award_complaint_document = snitch(put_tender_lots_award_complaint_document)
    test_patch_tender_lots_award_complaint_document = snitch(patch_tender_lots_award_complaint_document)


class TenderStage2UAAwardDocumentResourceTest(BaseTenderUAAwardPendingTest, TenderAwardDocumentResourceTestMixin):
    initial_lots = test_tender_cd_lots


class TenderStage2UA2LotAwardDocumentResourceTest(
    BaseTenderUAAwardPendingTest, Tender2LotAwardDocumentResourceTestMixin
):
    initial_lots = deepcopy(2 * test_tender_cd_lots)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EU2LotAwardComplaintDocumentResourceTest)
    )
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EU2LotAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EU2LotAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EU2LotAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EULotAwardResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
