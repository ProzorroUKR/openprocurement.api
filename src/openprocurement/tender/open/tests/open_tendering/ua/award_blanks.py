from openprocurement.tender.core.constants import QUALIFICATION_ACTIVATION_BLOCKING_CRITERIA
from openprocurement.tender.core.tests.utils import change_auth


def award_activation_blocked_by_exclusion_criteria(self):
    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    requirement_ids = {
        criterion["classification"]["id"]: criterion["requirementGroups"][0]["requirements"][0]["id"]
        for criterion in response.json["data"]
        if criterion["classification"]["id"] in QUALIFICATION_ACTIVATION_BLOCKING_CRITERIA
    }
    self.assertEqual(set(requirement_ids), set(QUALIFICATION_ACTIVATION_BLOCKING_CRITERIA))

    award_path = "/tenders/{}/awards/{}".format(self.tender_id, self.award_id)
    response = self.app.post_json(
        "{}/requirement_responses?acc_token={}".format(award_path, self.tender_token),
        {"data": [{"requirement": {"id": req_id}, "value": True} for req_id in requirement_ids.values()]},
    )
    self.assertEqual(response.status, "201 Created")
    response_ids = {rr["requirement"]["id"]: rr["id"] for rr in response.json["data"]}

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")

    def activate(status=None):
        with change_auth(self.app, ("Basic", ("token", ""))):
            return self.app.patch_json(
                award_path,
                {"data": {"status": "active", "qualified": True, "eligible": True}},
                status=status,
            )

    still_blocking = set(QUALIFICATION_ACTIVATION_BLOCKING_CRITERIA)
    for classification_id in sorted(QUALIFICATION_ACTIVATION_BLOCKING_CRITERIA):
        response = activate(status=422)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "requirementResponses",
                    "description": "Can't update award to active status with positive response to criteria: {}".format(
                        ", ".join(sorted(still_blocking))
                    ),
                }
            ],
        )
        self.app.patch_json(
            "{}/requirement_responses/{}?acc_token={}".format(
                award_path, response_ids[requirement_ids[classification_id]], self.tender_token
            ),
            {"data": {"value": False}},
        )
        still_blocking.remove(classification_id)

    response = activate()
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
