from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.utils import calculate_tender_business_date
from datetime import timedelta
from dateutil.parser import parse as parse_date
from mock import patch


class TenderQualificationMilestoneMixin(object):
    context_name = "qualification"  # can be also "award"
    initial_bids_tokens = {}
    context_id = None
    tender_id = None
    tender_token = None
    app = None

    def setUp(self):
        super(TenderQualificationMilestoneMixin, self).setUp()
        if self.context_name == "qualification":
            response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
            self.assertEqual(response.content_type, "application/json")
            qualifications = response.json["data"]
            self.context_id = qualifications[0]["id"]
        else:
            self.context_id = self.award_id

    def test_24hours_milestone(self):
        self.app.authorization = ("Basic", ("broker", ""))

        # try upload documents
        response = self.app.get("/tenders/{}".format(self.tender_id))
        context = response.json["data"]["{}s".format(self.context_name)][0]
        bid_id = context.get("bid_id") or context.get("bidID")  # awards and qualifications developed on different days
        winner_token = self.initial_bids_tokens[bid_id]
        upload_allowed_by_default = response.json["data"]["procurementMethodType"] == "aboveThresholdUA.defense"
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
            status=403
        )
        print(get_now() > RELEASE_2020_04_19)
        print(get_now() > RELEASE_2020_04_19)
        if get_now() > RELEASE_2020_04_19:
            self.assertEqual(
                response.json,
                {"status": "error", "errors": [{"description": "The only allowed milestone code is '24h'",
                                                "location": "body", "name": "data"}]}
            )
        else:
            print(response.json)
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
        expected_date = calculate_tender_business_date(
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
                        "description": "Can't change status to 'active' "
                                       "until milestone.dueDate: {}".format(created_milestone["dueDate"]),
                        "location": "body", "name": "data"
                    }]
            }
        )

        # try upload documents
        self.assert_upload_docs_status(bid_id, winner_token)

        # wait until milestone dueDate ends
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
        tender = self.db.get(self.tender_id)
        context = tender["{}s".format(self.context_name)][0]
        context["milestones"] = []
        self.db.save(tender)

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
        response = self.app.post(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(
                self.tender_id, bid_id, bid_token),
            upload_files=[("file", "name.doc", "content")],
            status=201 if success else 403
        )
        if success:  #
            self.app.put(
                "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                    self.tender_id, bid_id, response.json["data"]["id"], bid_token),
                upload_files=[("file", "ham.jpeg", "content3")],
            )
            self.app.patch_json(
                "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                    self.tender_id, bid_id, response.json["data"]["id"], bid_token),
                {"data": {"title": "spam.doc"}},
                status=200 if success else 403
            )
