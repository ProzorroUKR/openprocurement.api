from datetime import timedelta
from unittest import mock

from openprocurement.api.utils import get_now


def delete_requirement_evidence(self):
    self.set_status("draft")
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
        ),
        {"data": self.test_evidence_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    base_request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences".format(
        self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, evidence_id, self.tender_token
    )

    response = self.app.delete("{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token))

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
        ),
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
        ),
        {"data": self.test_evidence_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    self.set_status("active.enquiries")

    with mock.patch(
        "openprocurement.tender.requestforproposal.procedure.state"
        ".criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
        get_now() - timedelta(days=1),
    ):
        response = self.app.delete(
            "{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': "Can't delete object if tender not in " "['draft'] statuses",
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )

        self.set_status("active.auction")
        with mock.patch(
            "openprocurement.tender.requestforproposal.procedure.state"
            ".criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
            get_now() + timedelta(days=1),
        ):
            response = self.app.delete(
                "{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token),
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["status"], "error")
            self.assertEqual(
                response.json["errors"],
                [
                    {
                        'description': "Can't delete object if tender not in " "['draft', 'active.enquiries'] statuses",
                        'location': 'body',
                        'name': 'data',
                    }
                ],
            )
            with mock.patch(
                "openprocurement.tender.requestforproposal.procedure.state"
                ".criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
                get_now() - timedelta(days=1),
            ):
                response = self.app.delete(
                    "{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token),
                    status=403,
                )
                self.assertEqual(response.status, "403 Forbidden")
                self.assertEqual(response.content_type, "application/json")
                self.assertEqual(response.json["status"], "error")
                self.assertEqual(
                    response.json["errors"],
                    [
                        {
                            'description': "Can't delete object if tender not in " "['draft'] statuses",
                            'location': 'body',
                            'name': 'data',
                        }
                    ],
                )


def put_rg_requirement_invalid(self):
    post_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}"
    put_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}"
    response = self.app.post_json(
        post_url.format(self.tender_id, self.criteria_id, self.rg_id, self.tender_token),
        {"data": self.test_requirement_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.requirement_id = response.json["data"]["id"]

    with mock.patch(
        "openprocurement.tender.requestforproposal.procedure.state."
        "criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
        get_now() + timedelta(days=1),
    ):
        response = self.app.put_json(
            put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
            {"data": {}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{'description': 'Forbidden', 'location': 'body', 'name': 'data'}],
        )

    with mock.patch(
        "openprocurement.tender.requestforproposal.procedure.state"
        ".criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
        get_now() - timedelta(days=1),
    ):
        self.set_status("active.auction")
        response = self.app.put_json(
            put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
            {"data": {}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Can't put object if tender not in {} statuses".format(self.allowed_put_statuses),
                }
            ],
        )
