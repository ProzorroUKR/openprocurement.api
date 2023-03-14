from copy import deepcopy
from uuid import uuid4

from openprocurement.api.context import set_now
from openprocurement.api.tests.base import change_auth
from openprocurement.api.utils import get_now
from openprocurement.framework.electroniccatalogue.models import Framework
from openprocurement.framework.electroniccatalogue.tests.base import non_active_cpb_id


def simple_add_framework(self):
    set_now()

    u = Framework(self.initial_data)
    u.prettyID = "UA-F"
    u.dateModified = get_now().isoformat()

    assert u.id is None
    assert u.rev is None

    u.id = uuid4().hex
    self.mongodb.frameworks.save(u, insert=True)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.mongodb.frameworks.get(u.id)

    assert u.prettyID == fromdb["prettyID"]
    assert u.doc_type is None

    self.mongodb.frameworks.delete(u.id)

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
                'description': {'kind': ["Value must be one of ['central']."]},
                'location': 'body', 'name': 'procuringEntity'
            }
        ],
    )


def cpb_standard_status(self):
    response = self.app.post_json("/frameworks", {"data": self.initial_data})
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
                'location': 'body', 'name': 'procuringEntity'
            }
        ],
    )


def accreditation_level(self):
    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post_json("/frameworks", {"data": self.initial_data}, status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{"location": "url", "name": "accreditation",
              "description": "Broker Accreditation level does not permit framework creation"}],
        )

    with change_auth(self.app, ("Basic", ("broker2", ""))):
        response = self.app.post_json("/frameworks", {"data": self.initial_data}, status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{"location": "url", "name": "accreditation",
              "description": "Broker Accreditation level does not permit framework creation"}],
        )

    with change_auth(self.app, ("Basic", ("broker3", ""))):
        response = self.app.post_json("/frameworks", {"data": self.initial_data}, status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{"location": "url", "name": "accreditation",
              "description": "Broker Accreditation level does not permit framework creation"}],
        )

    with change_auth(self.app, ("Basic", ("broker4", ""))):
        response = self.app.post_json("/frameworks", {"data": self.initial_data}, status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{"location": "url", "name": "accreditation",
              "description": "Broker Accreditation level does not permit framework creation"}],
        )

    with change_auth(self.app, ("Basic", ("broker5", ""))):
        response = self.app.post_json("/frameworks", {"data": self.initial_data})
        self.assertEqual(response.status, "201 Created")
