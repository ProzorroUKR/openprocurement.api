from uuid import uuid4

from openprocurement.api.context import set_now
from openprocurement.api.utils import get_now
from openprocurement.contracting.econtract.procedure.models.contract import PostContract


def create_contract(self, data):
    if "id" not in data and "_id" not in data:
        data["id"] = uuid4().hex
    set_now(get_now())
    self.mongodb.contracts.save(PostContract(data).serialize(), insert=True)
    response = self.app.get(f"/contracts/{data['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    return response.json["data"]
