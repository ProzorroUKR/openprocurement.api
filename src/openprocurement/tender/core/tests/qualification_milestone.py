from openprocurement.api.utils import get_now, parse_date
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.utils import calculate_tender_date, calculate_complaint_business_date
from openprocurement.tender.core.constants import ALP_MILESTONE_REASONS
from copy import deepcopy
from datetime import timedelta
from mock import patch


class BaseTenderMilestone24HMixin:
    docservice = True

    context_name = None
    initial_bids_tokens = {}
    context_id = None
    tender_id = None
    tender_token = None
    app = None

    def setUp(self):
        super(BaseTenderMilestone24HMixin, self).setUp()
        if self.context_name == "qualification":
            response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
            self.assertEqual(response.content_type, "application/json")
            qualifications = response.json["data"]
            self.context_id = qualifications[0]["id"]
        else:
            self.context_id = self.award_id

    def test_24hours_milestone(self):
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}".format(self.tender_id))
        procurement_method_type = response.json["data"]["procurementMethodType"]

        # try upload documents
        context = response.json["data"]["{}s".format(self.context_name)][0]
        bid_id = context.get("bid_id") or context.get("bidID")  # awards and qualifications developed on different days
        winner_token = self.initial_bids_tokens[bid_id]
        upload_allowed_by_default = procurement_method_type in (
            "aboveThresholdUA.defense",
            "simple.defense",
            "belowThreshold",
        )
        self.assert_upload_docs_status(bid_id, winner_token, success=upload_allowed_by_default)

        # invalid creation
        response = self.app.post_json(
            "/tenders/{}/{}s/{}/milestones".format(self.tender_id, self.context_name, self.context_id),
            {
                "data": {}
            },
            status=403
        )
        self.assertEqual(
            response.json,
            {"status": "error", "errors": [{"location": "url", "name": "permission", "description": "Forbidden"}]}
        )
        response = self.app.post_json(
            "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
                self.tender_id,
                self.context_name,
                self.context_id,
                self.tender_token
            ),
            {
                "data": {
                    "code": "alp"
                }
            },
            status=422
        )
        if get_now() > RELEASE_2020_04_19:
            self.assertEqual(
                response.json,
                {"status": "error", "errors": [{
                    "location": "body",
                    "name": "code",
                    "description": [
                        "Value must be one of ['24h']."
                    ]
                }]}
            )
        else:
            self.assertEqual(
                response.json,
                {"status": "error", "errors": [{"location": "body", "name": "data", "description": "Forbidden"}]}
            )
            return

        # valid creation
        request_data = {
            "code": "24h",
            "description": "One ring to bring them all and in the darkness bind them",
            "dueDate": (get_now() + timedelta(days=10)).isoformat()
        }
        response = self.app.post_json(
            "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
                self.tender_id, self.context_name, self.context_id, self.tender_token
            ),
            {"data": request_data},
        )
        self.assertEqual(response.status, "201 Created")
        created_milestone = response.json["data"]

        # get milestone from tender
        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender_data = response.json["data"]
        context = tender_data["{}s".format(self.context_name)][0]
        public_milestone = context["milestones"][0]

        self.assertEqual(created_milestone, public_milestone)
        self.assertEqual(
            set(created_milestone.keys()),
            {
                "id",
                "date",
                "code",
                "description",
                "dueDate",
            }
        )
        self.assertEqual(created_milestone["code"], request_data["code"])
        self.assertEqual(created_milestone["description"], request_data["description"])
        self.assertNotEqual(created_milestone["dueDate"], request_data["dueDate"])
        expected_date = calculate_tender_date(
            parse_date(created_milestone["date"]),
            timedelta(hours=24),
            tender_data
        )
        self.assertEqual(created_milestone["dueDate"], expected_date.isoformat())

        # get milestone by its direct link
        response = self.app.get("/tenders/{}/{}s/{}/milestones/{}".format(
            self.tender_id, self.context_name, self.context_id, created_milestone["id"]
        ))
        direct_milestone = response.json["data"]
        self.assertEqual(created_milestone, direct_milestone)

        # can't post another
        response = self.app.post_json(
            "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
                self.tender_id, self.context_name, self.context_id, self.tender_token
            ),
            {"data": request_data},
            status=422
        )
        self.assertEqual(
            response.json,
            {"status": "error", "errors": [{"description": [
                {"milestones": ["There can be only one '24h' milestone"]}],
                 "location": "body", "name": "{}s".format(self.context_name)}]}
        )

        # can't update status of context until dueDate
        if procurement_method_type in ("belowThreshold",):
            activation_data = {"status": "active"}
        else:
            activation_data = {"status": "active", "qualified": True, "eligible": True}
        response = self.app.patch_json(
            "/tenders/{}/{}s/{}?acc_token={}".format(
                self.tender_id, self.context_name, self.context_id, self.tender_token
            ),
            {"data": activation_data},
            status=403
        )
        self.assertEqual(
            response.json,
            {
                "status": "error", "errors": [
                    {
                        "description": (
                            "Can't change status to 'active' "
                            "until milestone.dueDate: {}".format(created_milestone["dueDate"])
                        ),
                        "location": "body", "name": "data"
                    }]
            }
        )

        # try upload documents
        self.assert_upload_docs_status(bid_id, winner_token)

        # wait until milestone dueDate ends
        with patch("openprocurement.tender.core.procedure.validation.get_now", lambda: get_now() + timedelta(hours=24)):
            with patch("openprocurement.tender.core.validation.get_now", lambda: get_now() + timedelta(hours=24)):
                self.assert_upload_docs_status(bid_id, winner_token, success=upload_allowed_by_default)

                response = self.app.patch_json(
                    "/tenders/{}/{}s/{}?acc_token={}".format(
                        self.tender_id, self.context_name, self.context_id, self.tender_token
                    ),
                    {"data": activation_data},
                    status=200
                )
                self.assertEqual(response.json["data"]["status"], "active")

        # check appending milestone at active qualification status
        # remove milestone to skip "only one" validator
        tender = self.mongodb.tenders.get(self.tender_id)
        context = tender["{}s".format(self.context_name)][0]
        context["milestones"] = []
        self.mongodb.tenders.save(tender)

        response = self.app.post_json(
            "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
                self.tender_id, self.context_name, self.context_id, self.tender_token
            ),
            {"data": request_data},
            status=403
        )
        self.assertEqual(
            response.json,
            {"status": "error", "errors": [
                {"description": "Not allowed in current 'active' {} status".format(self.context_name),
                 "location": "body", "name": "data"}]}
        )

    def assert_upload_docs_status(self, bid_id, bid_token, success=True):
        document = {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
        response = self.app.post_json(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(
                self.tender_id, bid_id, bid_token),
            {"data": document},
            status=201 if success else 403
        )
        if success:  #
            document["title"] = "ham.jpeg"
            self.app.put_json(
                "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                    self.tender_id, bid_id, response.json["data"]["id"], bid_token),
                {"data": document},
            )
            self.app.patch_json(
                "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                    self.tender_id, bid_id, response.json["data"]["id"], bid_token),
                {"data": {"title": "spam.doc"}},
                status=200 if success else 403
            )


class TenderQualificationMilestone24HMixin(BaseTenderMilestone24HMixin):
    context_name = "qualification"


class TenderAwardMilestone24HMixin(BaseTenderMilestone24HMixin):
    context_name = "award"

    def test_24hours_milestone_unsuccessful_award(self):
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}".format(self.tender_id))
        procurement_method_type = response.json["data"]["procurementMethodType"]

        # valid creation
        request_data = {
            "code": "24h",
            "description": "One ring to bring them all and in the darkness bind them",
            "dueDate": (get_now() + timedelta(days=10)).isoformat()
        }
        response = self.app.post_json(
            "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
                self.tender_id, self.context_name, self.context_id, self.tender_token
            ),
            {"data": request_data},
        )
        self.assertEqual(response.status, "201 Created")
        created_milestone = response.json["data"]

        # wait until milestone dueDate ends
        with patch("openprocurement.tender.core.procedure.validation.get_now", lambda: get_now() + timedelta(hours=24)):
            with patch("openprocurement.tender.core.validation.get_now", lambda: get_now() + timedelta(hours=24)):
                response = self.app.patch_json(
                    "/tenders/{}/{}s/{}?acc_token={}".format(
                        self.tender_id, self.context_name, self.context_id, self.tender_token
                    ),
                    {"data": {"status": "unsuccessful"}},
                    status=200
                )
                self.assertEqual(response.json["data"]["status"], "unsuccessful")

        # check appending milestone at active qualification status
        # remove milestone to skip "only one" validator
        tender = self.mongodb.tenders.get(self.tender_id)
        context = tender["{}s".format(self.context_name)][0]
        context["milestones"] = []
        self.mongodb.tenders.save(tender)

        response = self.app.post_json(
            "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
                self.tender_id, self.context_name, self.context_id, self.tender_token
            ),
            {"data": request_data},
            status=403
        )
        self.assertEqual(
            response.json,
            {"status": "error", "errors": [
                {"description": "Not allowed in current 'unsuccessful' {} status".format(self.context_name),
                 "location": "body", "name": "data"}]}
        )

    def test_24hours_milestone_cancelled_award(self):
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}".format(self.tender_id))
        procurement_method_type = response.json["data"]["procurementMethodType"]

        # valid creation
        request_data = {
            "code": "24h",
            "description": "One ring to bring them all and in the darkness bind them",
            "dueDate": (get_now() + timedelta(days=10)).isoformat()
        }
        response = self.app.post_json(
            "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
                self.tender_id, self.context_name, self.context_id, self.tender_token
            ),
            {"data": request_data},
        )
        self.assertEqual(response.status, "201 Created")
        created_milestone = response.json["data"]

        # can't update status of context until dueDate
        if procurement_method_type in ("belowThreshold",):
            activation_data = {"status": "active"}
        else:
            activation_data = {"status": "active", "qualified": True, "eligible": True}

        # wait until milestone dueDate ends
        with patch("openprocurement.tender.core.procedure.validation.get_now", lambda: get_now() + timedelta(hours=24)):
            with patch("openprocurement.tender.core.validation.get_now", lambda: get_now() + timedelta(hours=24)):
                response = self.app.patch_json(
                    "/tenders/{}/{}s/{}?acc_token={}".format(
                        self.tender_id, self.context_name, self.context_id, self.tender_token
                    ),
                    {"data": activation_data},
                    status=200
                )
                self.assertEqual(response.json["data"]["status"], "active")
                response = self.app.patch_json(
                    "/tenders/{}/{}s/{}?acc_token={}".format(
                        self.tender_id, self.context_name, self.context_id, self.tender_token
                    ),
                    {"data": {"status": "cancelled"}},
                )

        # check appending milestone at active qualification status
        # remove milestone to skip "only one" validator
        tender = self.mongodb.tenders.get(self.tender_id)
        context = tender["{}s".format(self.context_name)][0]
        context["milestones"] = []
        self.mongodb.tenders.save(tender)

        response = self.app.post_json(
            "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
                self.tender_id, self.context_name, self.context_id, self.tender_token
            ),
            {"data": request_data},
            status=403
        )
        self.assertEqual(
            response.json,
            {"status": "error", "errors": [
                {"description": "Not allowed in current 'cancelled' {} status".format(self.context_name),
                 "location": "body", "name": "data"}]}
        )


class BaseTenderAwardMilestoneALPMixin:
    docservice = True

    initial_status = "active.auction"
    initial_bids_tokens = {}
    context_id = None
    tender_id = None
    tender_token = None
    app = None

    def setUp(self):
        more_bids = 4 - len(self.initial_bids)
        if more_bids > 0:
            self.initial_bids = deepcopy(self.initial_bids) + deepcopy(self.initial_bids)[:more_bids]
        self.initial_bids[0]["value"]["amount"] = 400
        self.initial_bids[1]["value"]["amount"] = 425
        self.initial_bids[2]["value"]["amount"] = 450
        self.initial_bids[3]["value"]["amount"] = 500
        self.assertEqual(len(self.initial_bids), 4)

        super(BaseTenderAwardMilestoneALPMixin, self).setUp()

        tender = self.mongodb.tenders.get(self.tender_id)
        for b in tender["bids"]:
            b["status"] = "active"
            if "lotValues" in b:
                for l in b["lotValues"]:
                    if "status" in l:
                        l["status"] = "active"  # in case they were "pending" #openeu
        self.mongodb.tenders.save(tender)

    def generate_auction_results(self):
        if self.initial_lots:
            auction_results = [
                {
                    "id": b["id"],
                    "lotValues": [{"relatedLot": l["relatedLot"], "value": l["value"]} for l in b["lotValues"]]
                } for b in self.initial_bids
            ]
            auction_results[0]["lotValues"][0]["value"]["amount"] = 200  # only 1 case
            auction_results[1]["lotValues"][0]["value"]["amount"] = 201  # both 1 and 2 case
            auction_results[2]["lotValues"][0]["value"]["amount"] = 350  # only 2 case
            auction_results[3]["lotValues"][0]["value"]["amount"] = 500  # no milestones
        else:
            auction_results = [
                {
                    "id": b["id"],
                    "value": b["value"]
                } for b in self.initial_bids
            ]
            auction_results[0]["value"]["amount"] = 29   # only 1 case
            auction_results[1]["value"]["amount"] = 30   # both 1 and 2 case
            auction_results[2]["value"]["amount"] = 350   # only 2 case
            auction_results[3]["value"]["amount"] = 500  # no milestones

        return auction_results

    def send_auction_results(self, auction_results):
        with change_auth(self.app, ("Basic", ("auction", ""))):
            if self.initial_lots:
                for l in self.initial_lots:
                    response = self.app.post_json(
                        f"/tenders/{self.tender_id}/auction/{l['id']}",
                        {"data": {"bids": auction_results}},
                        status=200
                    )
            else:
                response = self.app.post_json(
                    f"/tenders/{self.tender_id}/auction",
                    {"data": {"bids": auction_results}},
                    status=200
                )
        return response

    def find_award(self, awards, lot_id):
        for a in awards:
            if a["status"] == "pending" and a.get("lotID") == lot_id:
                return a


class TenderAwardMilestoneALPMixin(BaseTenderAwardMilestoneALPMixin):
    def test_milestone(self):
        """
        test alp milestone is created in two cases
        1. amount less by >=40% than mean of amount before auction
        2. amount less by >=30%  than the next amount
        :return:
        """
        auction_results = self.generate_auction_results()
        response = self.send_auction_results(auction_results)

        lot_id = self.initial_lots[0]["id"] if self.initial_lots else None

        tender = response.json["data"]
        self.assertEqual("active.qualification", tender["status"])
        self.assertGreater(len(tender["awards"]), 0)

        award = self.find_award(response.json["data"]["awards"], lot_id)

        bid_id = award["bid_id"]
        self.assertEqual(bid_id, auction_results[0]["id"])

        if get_now() < RELEASE_2020_04_19:
            return self.assertEqual(len(award.get("milestones", [])), 0)

        # check that a milestone's been created
        self.assertEqual(len(award.get("milestones", [])), 1)
        milestone = award["milestones"][0]
        self.assertEqual(milestone["code"], "alp")
        self.assertEqual(milestone["description"], ALP_MILESTONE_REASONS[0])

        # try to change award status
        unsuccessful_data = {"status": "unsuccessful"}
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(
                self.tender_id, award["id"], self.tender_token
            ),
            {"data": unsuccessful_data},
            status=403
        )
        tender = self.mongodb.tenders.get(self.tender_id)
        expected_due_date = calculate_complaint_business_date(
            parse_date(milestone["date"]),
            timedelta(days=1),
            tender,
            working_days=True,
        )
        self.assertEqual(
            response.json,
            {
                'status': 'error', 'errors': [{
                    'description': "Can't change status to 'unsuccessful' until milestone.dueDate: {}".format(
                        expected_due_date.isoformat()
                    ),
                    'location': 'body', 'name': 'data'
                }]
            }
        )

        # try to post/put/patch docs
        for doc_type in ["evidence", None]:
            self.assert_doc_upload(
                tender["procurementMethodType"], doc_type,
                bid_id, self.initial_bids_tokens[bid_id], expected_due_date
            )

        # setting "dueDate" to now
        self.wait_until_award_milestone_due_date()

        # after milestone dueDate tender owner can change award status
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(
                self.tender_id, award["id"], self.tender_token
            ),
            {"data": unsuccessful_data},
            status=200
        )
        self.assertEqual(response.json["data"]["status"], "unsuccessful")

        # check second award
        response = self.app.get(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            status=200
        )
        self.assertGreater(len(response.json["data"]), 1)

        second_award = self.find_award(response.json["data"], lot_id)

        self.assertEqual(len(second_award.get("milestones", [])), 1)
        self.assertEqual(second_award["milestones"][0]["description"], " / ".join(ALP_MILESTONE_REASONS))

        # proceed to the third award
        self.wait_until_award_milestone_due_date()
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(
                self.tender_id, second_award["id"], self.tender_token
            ),
            {"data": unsuccessful_data},
            status=200
        )
        self.assertEqual(response.json["data"]["status"], "unsuccessful")
        # checking 3rd award
        response = self.app.get(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            status=200
        )
        third_award = self.find_award(response.json["data"], lot_id)
        self.assertEqual(len(third_award.get("milestones", [])), 1)
        self.assertEqual(third_award["milestones"][0]["description"], ALP_MILESTONE_REASONS[1])

        # proceed to the last award
        self.wait_until_award_milestone_due_date()
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(
                self.tender_id, third_award["id"], self.tender_token
            ),
            {"data": unsuccessful_data},
            status=200
        )
        self.assertEqual(response.json["data"]["status"], "unsuccessful")
        # checking last award
        response = self.app.get(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            status=200
        )
        last_award = self.find_award(response.json["data"], lot_id)
        self.assertNotIn("milestones", last_award)

    def wait_until_award_milestone_due_date(self):
        tender = self.mongodb.tenders.get(self.tender_id)
        for a in tender["awards"]:
            if a.get("milestones"):
                a["milestones"][0]["dueDate"] = get_now().isoformat()
        self.mongodb.tenders.save(tender)

    def assert_doc_upload(self, procurement_method, doc_type, bid_id, bid_token, due_date):
        """
        expected that post/patch/put of docs is allowed during the period
        """
        response = self.app.post_json(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(
                self.tender_id, bid_id, bid_token),
            {"data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentType": doc_type
            }},
            status=201
        )
        document = response.json["data"]
        if doc_type is not None:
            self.assertEqual(document["documentType"], doc_type)
        else:
            self.assertNotIn("documentType", document)

        response = self.app.put_json(
            "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                self.tender_id, bid_id, document["id"], bid_token),
            {"data": {
                "title": "lorem(1).doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentType": doc_type,
            }},
            status=200
        )
        document = response.json["data"]
        self.assertEqual(document["title"], "lorem(1).doc")
        if doc_type is not None:
            self.assertEqual(document["documentType"], doc_type)
        else:
            self.assertNotIn("documentType", document)

        response = self.app.patch_json(
            "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                self.tender_id, bid_id, document["id"], bid_token),
            {"data": {"title": "Spam.json"}},
            status=200
        )
        document = response.json["data"]
        self.assertEqual(document["title"], "Spam.json")
        if doc_type is not None:
            self.assertEqual(document["documentType"], doc_type)
        else:
            self.assertNotIn("documentType", document)

        # can't post docs after milestone dueDate (except closeFrameworkAgreementUA)
        if procurement_method == "closeFrameworkAgreementUA":
            return

        with patch("openprocurement.tender.core.validation.get_now", lambda: due_date + timedelta(seconds=1)):
            with patch("openprocurement.tender.core.procedure.validation.get_now",
                       lambda: due_date + timedelta(seconds=1)):
                self.app.post_json(
                    "/tenders/{}/bids/{}/documents?acc_token={}".format(
                        self.tender_id, bid_id, bid_token),
                    {"data": {
                        "title": "name.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                        "documentType": doc_type
                    }},
                    status=403
                )
                self.app.put_json(
                    "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                        self.tender_id, bid_id, document["id"], bid_token),
                    {"data": {
                        "title": "lorem(5).doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                        "documentType": doc_type
                    }},
                    status=403
                )
                self.app.patch_json(
                    "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                        self.tender_id, bid_id, document["id"], bid_token),
                    {"data": {"title": "Spam(3).json"}},
                    status=403
                )


class TenderAwardMilestoneNoALPMixin(BaseTenderAwardMilestoneALPMixin):

    def test_no_milestone(self):
        auction_results = self.generate_auction_results()
        response = self.send_auction_results(auction_results)

        lot_id = self.initial_lots[0]["id"] if self.initial_lots else None

        tender = response.json["data"]
        self.assertGreater(len(tender["awards"]), 0)

        award = self.find_award(response.json["data"]["awards"], lot_id)
        bid_id = award["bid_id"]
        self.assertEqual(bid_id, auction_results[0]["id"])

        self.assertEqual(len(award.get("milestones", [])), 0)
