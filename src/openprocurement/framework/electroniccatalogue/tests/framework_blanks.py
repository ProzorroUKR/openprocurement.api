from copy import deepcopy

from openprocurement.api.tests.base import change_auth
from openprocurement.framework.electroniccatalogue.tests.base import non_active_cpb_id


def create_framework_draft_invalid_kind(self):
    request_path = "/frameworks"

    data = deepcopy(self.initial_data)
    data["procuringEntity"]["kind"] = "Не central"
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': {
                    'kind': [
                        "Value must be one of ('authority', 'central', 'defense', 'general', 'other', 'social', 'special')."
                    ]
                },
                'location': 'body',
                'name': 'procuringEntity',
            }
        ],
    )


def cpb_standard_status(self):
    response = self.app.post_json("/frameworks", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    data = deepcopy(self.initial_data)
    data["procuringEntity"]["identifier"]["id"] = non_active_cpb_id if non_active_cpb_id else "invalid_id"
    response = self.app.post_json("/frameworks", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': {'identifier': ["Can't create framework for inactive cpb"]},
                'location': 'body',
                'name': 'procuringEntity',
            }
        ],
    )


def accreditation_level(self):
    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post_json(
            "/frameworks", {"data": self.initial_data, "config": self.initial_config}, status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "url",
                    "name": "accreditation",
                    "description": "Broker Accreditation level does not permit framework creation",
                }
            ],
        )

    with change_auth(self.app, ("Basic", ("broker2", ""))):
        response = self.app.post_json(
            "/frameworks", {"data": self.initial_data, "config": self.initial_config}, status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "url",
                    "name": "accreditation",
                    "description": "Broker Accreditation level does not permit framework creation",
                }
            ],
        )

    with change_auth(self.app, ("Basic", ("broker3", ""))):
        response = self.app.post_json(
            "/frameworks", {"data": self.initial_data, "config": self.initial_config}, status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "url",
                    "name": "accreditation",
                    "description": "Broker Accreditation level does not permit framework creation",
                }
            ],
        )

    with change_auth(self.app, ("Basic", ("broker4", ""))):
        response = self.app.post_json(
            "/frameworks", {"data": self.initial_data, "config": self.initial_config}, status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "url",
                    "name": "accreditation",
                    "description": "Broker Accreditation level does not permit framework creation",
                }
            ],
        )

    with change_auth(self.app, ("Basic", ("broker5", ""))):
        response = self.app.post_json("/frameworks", {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
