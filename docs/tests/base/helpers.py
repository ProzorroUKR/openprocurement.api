from openprocurement.tender.core.tests.base import change_auth
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now


def complaint_create_pending(self, uri, data, token=None):
    url = "{}?acc_token={}".format(uri, token) if token else uri

    response = self.app.post_json(url, data)
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]
    complaint_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "{}/{}?acc_token={}".format(uri, complaint_id, complaint_token),
            {"data": {"status": "pending"}}
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "{}/{}".format(uri, complaint_id),
                {"data": {"status": "pending"}}
            )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    return complaint_id, complaint_token
