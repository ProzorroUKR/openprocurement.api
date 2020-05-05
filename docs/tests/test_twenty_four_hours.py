# -*- coding: utf-8 -*-
import os
from freezegun import freeze_time
from datetime import timedelta
from tests.base.constants import DOCS_URL, AUCTIONS_URL
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from openprocurement.api.utils import get_now
from openprocurement.tender.openua.tests.tender import BaseTenderUAWebTest
from openprocurement.tender.openua.tests.base import test_bids
from openprocurement.tender.core.tests.base import change_auth
from openprocurement.tender.belowthreshold.tests.base import test_organization


TARGET_DIR = 'docs/source/tendering/basic-actions/http/'


class TenderAwardMilestoneResourceTest(BaseTenderUAWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp
    relative_to = os.path.dirname(__file__)
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardMilestoneResourceTest, self).setUp()
        self.setUpMock()
        self.create_tender()
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {"data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "lotID": self.initial_bids[0]["lotValues"][0]["relatedLot"] if self.initial_lots else None,
                }},
            )
        award = response.json["data"]
        self.award_id = award["id"]

    def tearDown(self):
        self.tearDownMock()
        super(TenderAwardMilestoneResourceTest, self).tearDown()

    def test_milestone(self):
        self.app.authorization = ('Basic', ('broker', ''))

        # valid creation
        request_data = {
            "code": "24h",
            "description": "One ring to bring them all and in the darkness bind them"
        }
        with open(TARGET_DIR + '24hours/award-milestone-post.http', 'w') as self.app.file_obj:
            with freeze_time("2020-05-02 02:00:00"):
                response = self.app.post_json(
                    "/tenders/{}/awards/{}/milestones?acc_token={}".format(
                        self.tender_id, self.award_id, self.tender_token
                    ),
                    {"data": request_data},
                )
        self.assertEqual(response.status, "201 Created")

        with freeze_time("2020-05-02 02:00:01"):
            with open(TARGET_DIR + '24hours/award-patch.http', 'w') as self.app.file_obj:
                self.app.patch_json(
                    "/tenders/{}/awards/{}?acc_token={}".format(
                        self.tender_id, self.award_id, self.tender_token
                    ),
                    {"data": {"status": "active", "qualified": True, "eligible": True}},
                    status=403
                )

            # try upload documents
            response = self.app.get(
                "/tenders/{}/awards/{}?acc_token={}".format(
                    self.tender_id, self.award_id, self.tender_token
                )
            )
            context = response.json["data"]
            bid_id = context.get("bid_id")
            bid_token = self.initial_bids_tokens[bid_id]

            with open(TARGET_DIR + '24hours/post-doc.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    "/tenders/{}/bids/{}/documents?acc_token={}".format(
                        self.tender_id, bid_id, bid_token),
                    {
                        "data": {
                            "title": u"укр.doc",
                            "url": self.generate_docservice_url(),
                            "hash": "md5:" + "0" * 32,
                            "format": "application/msword",
                        }
                    },
                    status=201
                )

            with open(TARGET_DIR + '24hours/put-doc.http', 'w') as self.app.file_obj:
                self.app.put_json(
                    "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                        self.tender_id, bid_id, response.json["data"]["id"], bid_token
                    ),
                    {
                        "data": {
                            "title": u"укр.doc",
                            "url": self.generate_docservice_url(),
                            "hash": "md5:" + "0" * 32,
                            "format": "application/msword",
                        }
                    },
                    status=200
                )

        # qualification milestone creation
        tender = self.db.get(self.tender_id)
        tender["procurementMethodType"] = "aboveThresholdEU"
        tender["title_en"] = " "
        tender["procuringEntity"]["name_en"] = " "
        tender["procuringEntity"]["identifier"]["legalName_en"] = " "
        tender["procuringEntity"]["contactPoint"]["name_en"] = " "
        tender["status"] = "active.pre-qualification"
        tender_end = get_now() + timedelta(days=30, seconds=10)
        tender["tenderPeriod"]["endDate"] = tender_end.isoformat()
        tender["awardPeriod"]["startDate"] = tender_end.isoformat()
        qualification_id = "1234" * 8
        tender["qualifications"] = [
            {
                "id": qualification_id,
                "bidID": bid_id,
            }
        ]
        del tender["awards"]
        self.db.save(tender)

        with freeze_time("2020-05-02 02:00:20"):
            with open(TARGET_DIR + '24hours/qualification-milestone-post.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    "/tenders/{}/qualifications/{}/milestones?acc_token={}".format(
                        self.tender_id, qualification_id, self.tender_token
                    ),
                    {"data": request_data},
                )
        self.assertEqual(response.status, "201 Created")
