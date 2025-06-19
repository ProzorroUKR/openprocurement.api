from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_supplier


def qualified_eligible_awards(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
        {
            "data": {
                "suppliers": [test_tender_below_supplier],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[1]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")
    award_id = response.json["data"]["id"]
    # activate award without qualified and eligible
    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "qualified",
                "description": ["Can't update award to active status with not qualified"],
            }
        ],
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "active", "qualified": True}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update award to active status with not eligible",
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "active", "qualified": True, "eligible": False}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update award to active status with not eligible",
    )

    with patch(
        "openprocurement.tender.competitiveordering.procedure.state.award.NEW_ARTICLE_17_CRITERIA_REQUIRED",
        get_now() - timedelta(days=1),
    ):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active"}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "qualified",
                    "description": ["Can't update award to active status with not qualified"],
                }
            ],
        )

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "eligible": True}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"][0]["description"],
            ["Can't update award to active status with not qualified"],
        )

        # after NEW_ARTICLE_17_CRITERIA_REQUIRED required only qualified: True
        # successful activation
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True}},
        )

        # cancel the winner
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
            {"data": {"status": "cancelled"}},
        )

        # set award to unsuccessful status without qualified or eligible False
        new_award = self.app.get(f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}").json["data"][-1]
        new_award_id = new_award["id"]
        self.assertEqual(new_award["status"], "pending")

        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{new_award_id}?acc_token={self.tender_token}",
            {"data": {"status": "unsuccessful", "qualified": True}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update award to unsuccessful status when qualified/eligible isn't set to False",
        )

        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{new_award_id}?acc_token={self.tender_token}",
            {"data": {"status": "unsuccessful", "qualified": True}},
            status=422,
        )

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{new_award_id}?acc_token={self.tender_token}",
            {"data": {"status": "unsuccessful", "qualified": False, "eligible": True}},
            status=422,
        )
        self.assertEqual(
            response.json["errors"][0], {'location': 'body', 'name': 'eligible', 'description': 'Rogue field'}
        )

        # successful setting unsuccessful
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{new_award_id}?acc_token={self.tender_token}",
            {"data": {"status": "unsuccessful", "qualified": False}},
        )
