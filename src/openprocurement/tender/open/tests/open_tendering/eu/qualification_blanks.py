from openprocurement.tender.core.constants import QUALIFICATION_ACTIVATION_BLOCKING_CRITERIA


def qualification_activation_blocked_by_exclusion_criteria(self):
    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    requirement_ids = {
        criterion["classification"]["id"]: criterion["requirementGroups"][0]["requirements"][0]["id"]
        for criterion in response.json["data"]
        if criterion["classification"]["id"] in QUALIFICATION_ACTIVATION_BLOCKING_CRITERIA
    }
    self.assertEqual(set(requirement_ids), set(QUALIFICATION_ACTIVATION_BLOCKING_CRITERIA))

    qualification_path = "/tenders/{}/qualifications/{}".format(self.tender_id, self.qualification_id)
    response = self.app.post_json(
        "{}/requirement_responses?acc_token={}".format(qualification_path, self.tender_token),
        {"data": [{"requirement": {"id": req_id}, "value": True} for req_id in requirement_ids.values()]},
    )
    self.assertEqual(response.status, "201 Created")
    response_ids = {rr["requirement"]["id"]: rr["id"] for rr in response.json["data"]}

    def activate(status=None):
        return self.app.patch_json(
            "{}?acc_token={}".format(qualification_path, self.tender_token),
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
                    "description": (
                        "Can't update qualification to active status with positive response to criteria: {}".format(
                            ", ".join(sorted(still_blocking))
                        )
                    ),
                }
            ],
        )
        self.app.patch_json(
            "{}/requirement_responses/{}?acc_token={}".format(
                qualification_path, response_ids[requirement_ids[classification_id]], self.tender_token
            ),
            {"data": {"value": False}},
        )
        still_blocking.remove(classification_id)

    response = activate()
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
