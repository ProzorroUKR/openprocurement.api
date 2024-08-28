import json
import os
from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from openprocurement.api.constants import (
    RELEASE_2020_04_19,
    RELEASE_ECRITERIA_ARTICLE_17,
    SANDBOX_MODE,
)
from openprocurement.api.procedure.utils import apply_data_patch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
)
from openprocurement.tender.belowthreshold.tests.utils import (
    set_bid_lotvalues,
    set_tender_lots,
)
from openprocurement.tender.cfaua.constants import MIN_BIDS_NUMBER, TENDERING_DAYS
from openprocurement.tender.cfaua.tests.periods import PERIODS
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_with_complaints_after_2020_04_19,
)
from openprocurement.tender.core.utils import calculate_tender_full_date
from openprocurement.tender.openua.tests.base import (
    BaseTenderUAWebTest as BaseBaseTenderWebTest,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
now = get_now()

# Prepare test_bids_data
with open(os.path.join(BASE_DIR, "data/test_bids.json")) as fd:
    test_tender_cfaua_bids = json.load(fd)
    test_tender_cfaua_bids = [deepcopy(test_tender_cfaua_bids[0]) for _ in range(MIN_BIDS_NUMBER)]
    for num, test_bid in enumerate(test_tender_cfaua_bids):
        if get_now() > RELEASE_ECRITERIA_ARTICLE_17:
            del test_bid["selfEligible"]
        test_bid["value"]["amount"] = test_bid["value"]["amount"] + num * 1

# Prepare test_features_tender_data
with open(os.path.join(BASE_DIR, "data/test_tender.json")) as fd:
    test_tender_cfaua_data = json.load(fd)
    test_tender_cfaua_data["tenderPeriod"]["endDate"] = (now + timedelta(days=TENDERING_DAYS + 1)).isoformat()


# Prepare features_tender
with open(os.path.join(BASE_DIR, "data/test_features.json")) as fd:
    test_tender_cfaua_features_data = test_tender_cfaua_data.copy()
    test_tender_cfaua_features_item = test_tender_cfaua_features_data["items"][0].copy()
    test_tender_cfaua_features_item["id"] = "1"
    test_tender_cfaua_features_data["items"] = [test_tender_cfaua_features_item]
    test_tender_cfaua_features_data["features"] = json.load(fd)
    test_tender_cfaua_features_bids = deepcopy(test_tender_cfaua_bids)
    for x, bid in enumerate(test_tender_cfaua_features_bids):
        bid["parameters"] = [{"code": i["code"], "value": 0.1} for i in test_tender_cfaua_features_data["features"]]

test_tender_cfaua_features_bids_same_amount = deepcopy(test_tender_cfaua_features_bids)
for bid in test_tender_cfaua_features_bids_same_amount:
    bid["value"]["amount"] = 469

# Prepare features_tender
with open(os.path.join(BASE_DIR, "data/test_lots.json")) as fd:
    test_tender_cfaua_lots = json.load(fd)


# Prepare data for tender with lot
test_tender_cfaua_with_lots_data = deepcopy(test_tender_cfaua_data)
set_tender_lots(test_tender_cfaua_with_lots_data, test_tender_cfaua_lots)

test_tender_cfaua_lots_with_ids = deepcopy(test_tender_cfaua_with_lots_data["lots"])
test_tender_cfaua_bids_with_lotvalues = deepcopy(test_tender_cfaua_bids)
for bid in test_tender_cfaua_bids_with_lotvalues:
    set_bid_lotvalues(bid, test_tender_cfaua_lots_with_ids)


start_date = get_now()

test_tender_cfaua_agreement_period = {
    "startDate": start_date.isoformat(),
    "endDate": (start_date + timedelta(days=4 * 365)).isoformat(),
}

if SANDBOX_MODE:
    test_tender_cfaua_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_cfaua_config = {
    "hasAuction": True,
    "hasAwardingOrder": True,
    "hasValueRestriction": True,
    "valueCurrencyEquality": True,
    "hasPrequalification": True,
    "minBidsNumber": 3,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": True,
    "hasAwardComplaints": True,
    "hasCancellationComplaints": True,
    "hasValueEstimation": True,
    "hasQualificationComplaints": True,
    "tenderComplainRegulation": 4,
    "qualificationComplainDuration": 5,
    "awardComplainDuration": 10,
    "cancellationComplainDuration": 10,
    "clarificationUntilDuration": 3,
    "qualificationDuration": 20,
    "restricted": False,
}


class BaseTenderWebTest(BaseBaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    backup_attr_keys = [
        "initial_data",
        "initial_status",
        "initial_bids",
        "initial_lots",
        "initial_auth",
        "meta_initial_bids",
        "meta_initial_lots",
    ]
    min_bids_number = MIN_BIDS_NUMBER
    initial_data = deepcopy(test_tender_cfaua_data)
    initial_config = test_tender_cfaua_config
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None
    initial_auth = None

    meta_initial_bids = deepcopy(test_tender_cfaua_bids)
    meta_initial_lots = deepcopy(test_tender_cfaua_lots)

    periods = PERIODS

    forbidden_agreement_document_modification_actions_status = (
        "unsuccessful"  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    )
    forbidden_question_add_actions_status = (
        "active.pre-qualification"  # status, in which adding tender questions is forbidden
    )
    forbidden_question_update_actions_status = (
        "active.pre-qualification"  # status, in which updating tender questions is forbidden
    )
    question_claim_block_status = "active.pre-qualification"  # status, tender cannot be switched to while it has questions/complaints related to its lot
    # auction role actions
    forbidden_auction_actions_status = "active.pre-qualification.stand-still"  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = (
        "active.pre-qualification.stand-still"  # status, in which adding document to tender auction is forbidden
    )

    @classmethod
    def setUpClass(cls):
        super(BaseBaseTenderWebTest, cls).setUpClass()
        cls.backup_pure_data()

    @classmethod
    def backup_pure_data(cls):
        for attr in cls.backup_attr_keys:
            setattr(cls, "_{}".format(attr), deepcopy(getattr(cls, attr)))

    def restore_pure_data(self):
        for key in self.backup_attr_keys:
            setattr(self, key, deepcopy(getattr(self, "_{}".format(key))))

    def convert_bids_for_tender_with_lots(self, bids, lots):
        for bid in bids:
            set_bid_lotvalues(bid, lots)

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", startend="enquiry_end")

    def set_complaint_period_end(self):
        self.set_status("active.tendering", startend="end")

    def setUp(self):
        super(BaseBaseTenderWebTest, self).setUp()
        self.app.authorization = self.initial_auth or ("Basic", ("broker", ""))

    def tearDown(self):
        super().tearDown()
        self.restore_pure_data()

    def generate_bids(self, status, startend):
        tenderPeriod_startDate = self.now + self.periods[status][startend]["tenderPeriod"]["startDate"]
        bids = self.tender_document.get("bids", [])
        lots = self.tender_document.get("lots", [])
        numberOfBids = len(bids)
        if not bids:
            self.tender_document_patch["bids"] = []
            if numberOfBids > 0:
                self.tender_document_patch["bids"] = self.tender_document["bids"]
            for position, meta_bid in enumerate(self.meta_initial_bids[numberOfBids:]):
                bid = deepcopy(meta_bid)
                if lots:
                    value = bid.pop("value")
                    bid["lotValues"] = [
                        {
                            "status": "pending",
                            "value": value,
                            "relatedLot": l["id"],
                            "date": (tenderPeriod_startDate + timedelta(seconds=(position + 1))).isoformat(),
                        }
                        for l in lots
                    ]
                bid.update(
                    {
                        "id": uuid4().hex,
                        "date": (tenderPeriod_startDate + timedelta(seconds=(position + 1))).isoformat(),
                        "owner_token": uuid4().hex,
                        "status": "pending",
                        "owner": "broker",
                    }
                )
                self.tender_document_patch["bids"].append(bid)
            self.save_changes()

    def generate_qualifications(self, status, startend):
        bids = self.tender_document.get("bids", [])
        lots = self.tender_document.get("lots", [])
        qualificationPeriod_startDate = self.now + self.periods[status][startend]["qualificationPeriod"]["startDate"]
        qualifications = self.tender_document.get("qualifications", [])
        active_lots = [lot["id"] for lot in lots if lot["status"] == "active"]
        active_bids = any(bid["status"] not in ["invalid", "deleted"] for bid in bids)
        if not qualifications:
            if active_bids:
                self.tender_document_patch["qualifications"] = []
                for bid in bids:
                    if bid.get("status") not in ["invalid", "deleted"]:
                        if lots:
                            for lotValue in bid["lotValues"]:
                                if (
                                    lotValue.get("status", "pending") == "pending"
                                    and lotValue["relatedLot"] in active_lots
                                ):
                                    self.tender_document_patch["qualifications"].append(
                                        {
                                            "id": uuid4().hex,
                                            "bidID": bid["id"],
                                            "status": "pending",
                                            "lotID": lotValue["relatedLot"],
                                            "date": qualificationPeriod_startDate.isoformat(),
                                            "qualified": False,
                                            "eligible": False,
                                        }
                                    )
                        else:
                            self.tender_document_patch["qualifications"].append(
                                {
                                    "id": uuid4().hex,
                                    "bidID": bid["id"],
                                    "status": "pending",
                                    "date": qualificationPeriod_startDate.isoformat(),
                                    "qualified": False,
                                    "eligible": False,
                                }
                            )
                self.save_changes()

    def activate_qualifications(self):
        qualifications = self.tender_document.get("qualifications", [])
        bids = self.tender_document.get("bids", [])
        lots = self.tender_document.get("lots", [])
        if qualifications and bids:
            self.tender_document_patch["bids"] = bids
            for index, qualification in enumerate(qualifications):
                if qualification["status"] == "pending":
                    qualification.update({"status": "active", "qualified": True, "eligible": True})
                    qualification["complaintPeriod"] = {
                        "startDate": get_now().isoformat(),
                        "endDate": calculate_tender_full_date(
                            get_now(),
                            timedelta(days=self.tender_document["config"]["qualificationComplainDuration"]),
                            tender=self.tender_document,
                        ).isoformat(),
                    }
                    for bid in self.tender_document_patch["bids"]:
                        if bid["id"] == qualification["bidID"]:
                            if lots:
                                any_lotValue_is_active = False
                                for lotValue in bid["lotValues"]:
                                    if (
                                        lotValue["status"] == "pending"
                                        and lotValue["relatedLot"] == qualification["lotID"]
                                    ):
                                        lotValue["status"] = "active"
                                        any_lotValue_is_active = True
                                if any_lotValue_is_active:
                                    bid["status"] = "active"
                            else:
                                bid["status"] = "active"
            self.tender_document_patch["qualifications"] = qualifications
            self.save_changes()

        # if self.tender_document.get('bids', ''):
        #     bids = self.tender_document['bids']
        #     for bid in bids:
        #         if bid['status'] == 'pending':
        #             bid.update({'status': 'active'})
        #     self.tender_document_patch.update({'bids': bids})

    def generate_awards(self, status, startend):
        maxAwards = self.tender_document.get("maxAwardsCount", 100000)
        bids = self.tender_document.get("bids", []) or self.tender_document_patch.get("bids", [])
        lots = self.tender_document.get("lots", []) or self.tender_document_patch.get("lots", [])
        awardPeriod_startDate = (self.now + self.periods[status][startend]["awardPeriod"]["startDate"]).isoformat()
        if "awards" not in self.tender_document:
            self.tender_document_patch["awards"] = []
            if lots:
                active_lots = {lot["id"]: 0 for lot in lots if lot["status"] == "active"}
                self.tender_document_patch["awards"] = []
                for bid in bids:
                    for lot_value in bid["lotValues"]:
                        if lot_value["relatedLot"] in active_lots:
                            if active_lots[lot_value["relatedLot"]] == maxAwards:
                                continue
                            award = {
                                "status": "pending",
                                "lotID": lot_value["relatedLot"],
                                "suppliers": bid["tenderers"],
                                "bid_id": bid["id"],
                                "value": lot_value["value"],
                                "date": awardPeriod_startDate,
                                "id": uuid4().hex,
                            }
                            self.tender_document_patch["awards"].append(award)
                            active_lots[lot_value["relatedLot"]] += 1

            else:
                for bid in bids:
                    award = {
                        "status": "pending",
                        "suppliers": bid["tenderers"],
                        "bid_id": bid["id"],
                        "value": bid["value"],
                        "date": awardPeriod_startDate,
                        "id": uuid4().hex,
                    }
                    self.tender_document_patch["awards"].append(award)
                    if len(self.tender_document_patch["awards"]) == maxAwards:
                        break
            self.save_changes()

    def activate_awards(self):
        awards = self.tender_document.get("awards", [])
        if awards:
            for award in awards:
                if award["status"] == "pending":
                    award.update({"status": "active"})
            self.tender_document_patch.update({"awards": awards})
            self.save_changes()

    def update_awards_complaint_periods(self, status, startend):
        AWARDS_COMPLAINTS_STATUSES = ("active.qualification.stand-still", "active.awarded", "complete")
        awards = self.tender_document.get("awards", [])
        awardPeriod = self.tender_document.get("awardPeriod", {})

        if awards and awardPeriod and status in AWARDS_COMPLAINTS_STATUSES:
            for award in awards:
                if award["status"] in ("unsuccessful", "active"):
                    award.update({"complaintPeriod": awardPeriod})
            self.tender_document_patch.update({"awards": awards})
            self.save_changes()

    def generate_agreement_data(self, lot=None):
        data = {
            "id": uuid4().hex,
            "items": (
                self.tender_document["items"]
                if not lot
                else [i for i in self.tender_document["items"] if i["relatedLot"] == lot["id"]]
            ),
            "agreementID": "{}-{}{}".format(
                self.tender_document["tenderID"], uuid4().hex, len(self.tender_document_patch["agreements"]) + 1
            ),
            "date": self.now.isoformat(),
            "contracts": [],
            "status": "pending",
        }
        unit_prices = [
            {
                "relatedItem": item["id"],
                "value": {
                    "currency": self.tender_document["value"]["currency"],
                    "valueAddedTaxIncluded": self.tender_document["value"]["valueAddedTaxIncluded"],
                },
            }
            for item in data["items"]
        ]
        for award in self.tender_document["awards"]:
            if lot and lot["id"] != award["lotID"]:
                continue
            if award["status"] != "active":
                continue
            data["contracts"].append(
                {
                    "id": uuid4().hex,
                    "suppliers": award["suppliers"],
                    "awardID": award["id"],
                    "bidID": award["bid_id"],
                    "date": get_now().isoformat(),
                    "unitPrices": unit_prices,
                    "status": "active",
                }
            )
        return data

    def generate_agreements(self, status, startend):
        if "agreements" not in self.tender_document:
            lots = self.tender_document.get("lots", [])
            awards = self.tender_document.get("awards", [])
            self.tender_document_patch["agreements"] = []
            if lots:
                for lot in lots:
                    if lot["status"] != "active":
                        continue
                    self.tender_document_patch["agreements"].append(self.generate_agreement_data(lot))
            else:
                self.tender_document_patch["agreements"].append(self.generate_agreement_data())
            self.save_changes()

    def activate_agreements(self, status, startend):
        for agreement in self.tender_document["agreements"]:
            self.tender_document_patch["agreements"] = []
            if agreement["status"] == "pending":
                for contract in agreement["contracts"]:
                    for unit_prices in contract["unitPrices"]:
                        unit_prices["value"]["amount"] = 93
                agreement["status"] = "active"
            self.tender_document_patch["agreements"].append(agreement)
            self.save_changes()

    def save_changes(self):
        if self.tender_document_patch:
            patch = apply_data_patch(self.tender_document, self.tender_document_patch)
            self.tender_document.update(patch)
            self.mongodb.tenders.save(self.tender_document)
            self.tender_document = self.mongodb.tenders.get(self.tender_id)
            self.tender_document_patch = {}

    def get_tender(self, role="token"):
        authorization = self.app.authorization
        self.app.authorization = ("Basic", (role, ""))
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.app.authorization = authorization
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        return response

    def set_status(self, status, startend="start", extra=None):
        self.now = get_now()
        self.tender_document = self.mongodb.tenders.get(self.tender_id)
        self.tender_document_patch = {"status": status}
        self.save_changes()
        if status == "active.tendering":
            self.update_periods(status, startend)

        elif status == "active.pre-qualification":
            self.update_periods(status, startend)
            # generate bids
            self.generate_bids(status, startend)
            # generate qualifications
            self.generate_qualifications(status, startend)

        elif status == "active.pre-qualification.stand-still":
            self.update_periods(status, startend)
            # generate bids
            self.generate_bids(status, startend)
            # generate qualifications
            self.generate_qualifications(status, startend)
            # activate qualifications and bids
            self.activate_qualifications()

            if startend == "end":
                self.update_qualification_complaint_periods()

        elif status == "active.auction":
            self.update_periods(status, startend)
            # generate bids
            self.generate_bids(status, startend)
            # generate qualifications
            self.generate_qualifications(status, startend)
            # activate qualifications and bids
            self.activate_qualifications()
            self.update_qualification_complaint_periods()

        elif status == "active.qualification":
            self.update_periods(status, startend)
            # generate bids
            self.generate_bids(status, startend)
            # generate qualifications
            self.generate_qualifications(status, startend)
            # activate qualifications and bids
            self.activate_qualifications()
            # generate awards
            self.generate_awards(status, startend)
            self.update_qualification_complaint_periods()

        elif status == "active.qualification.stand-still":
            self.update_periods(status, startend)
            # generate bids
            self.generate_bids(status, startend)
            # generate qualifications
            self.generate_qualifications(status, startend)
            # activate qualifications and bids
            self.activate_qualifications()
            # generate awards
            self.generate_awards(status, startend)
            self.activate_awards()
            self.update_awards_complaint_periods(status, startend)
            self.update_qualification_complaint_periods()

        elif status == "active.awarded":
            self.update_periods(status, startend)
            # generate bids
            self.generate_bids(status, startend)
            # generate qualifications
            self.generate_qualifications(status, startend)
            # activate qualifications and bids
            self.activate_qualifications()
            # generate awards
            self.generate_awards(status, startend)
            self.activate_awards()
            self.update_awards_complaint_periods(status, startend)
            self.generate_agreements(status, startend)
            self.update_qualification_complaint_periods()

            # generate_agreements()
        elif status == "complete":
            self.update_periods(status, startend)
            # generate bids
            self.generate_bids(status, startend)
            # generate qualifications
            self.generate_qualifications(status, startend)
            # activate qualifications and bids
            self.activate_qualifications()
            self.update_qualification_complaint_periods()
            # generate awards
            self.generate_awards(status, startend)
            self.activate_awards()
            self.update_awards_complaint_periods(status, startend)
            self.generate_agreements(status, startend)
            self.activate_agreements(status, startend)

        self.save_changes()
        return self.get_tender("chronograph")

    def prepare_awards(self):
        # switch to active.pre-qualification
        self.set_status("active.pre-qualification", extra={"id": self.tender_id, "status": "active.tendering"})
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
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status(
            "active.auction", extra={"id": self.tender_id, "status": "active.pre-qualification.stand-still"}
        )
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.auction")

        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        for b in auction_bids_data:
            b.pop("status", None)
        if self.initial_lots:
            for lot_id in self.initial_lots:
                response = self.app.post_json(
                    "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]), {"data": {"bids": auction_bids_data}}
                )
        else:
            response = self.app.post_json(
                "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": auction_bids_data}}
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "active.qualification")

    def cancel_tender(self, lot_id=None):
        """
        :param lot_id: id of lot for cancellation
        :return: None
        """
        cancellation = deepcopy(test_tender_below_cancellation)
        cancellation.update(
            {
                "status": "active",
            }
        )
        if lot_id:
            cancellation.update({"cancellationOf": "lot", "relatedLot": lot_id})
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        self.assertEqual(response.status, "201 Created")
        cancellation = response.json["data"]

        if get_now() < RELEASE_2020_04_19:
            self.assertEqual(cancellation["status"], "active")
        else:
            self.assertEqual(cancellation["status"], "draft")
            activate_cancellation_with_complaints_after_2020_04_19(self, cancellation["id"])

        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]
        if lot_id:
            for lot in tender["lots"]:
                if lot["id"] == lot_id:
                    self.assertEqual(lot["status"], "cancelled")
        else:
            self.assertEqual(tender["status"], "cancelled")


class BaseTenderContentWebTest(BaseTenderWebTest):
    initial_data = deepcopy(test_tender_cfaua_data)
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = deepcopy(test_tender_cfaua_lots)

    meta_initial_bids = deepcopy(test_tender_cfaua_bids)
    meta_initial_lots = deepcopy(test_tender_cfaua_lots)

    def setUp(self):
        super().setUp()
        self.create_tender()

        self.check_chronograph()
        # fixes tenders after inserting into fixture data
        # for ex auctionPeriod.shouldStartAfter is added


class BidsOverMaxAwardsMixin:
    initial_bids = deepcopy(test_tender_cfaua_bids) + deepcopy(test_tender_cfaua_bids)  # double testbids
    min_bids_number = MIN_BIDS_NUMBER * 2
