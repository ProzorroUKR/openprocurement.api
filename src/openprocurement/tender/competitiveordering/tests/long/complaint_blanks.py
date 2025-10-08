from copy import deepcopy

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_draft_complaint,
)
from openprocurement.tender.core.tests.utils import change_auth


def create_tender_complaint_for_restricted_tender(self):
    tender = self.mongodb.tenders.get(self.tender_id)
    tender["config"]["restricted"] = True
    self.mongodb.tenders.save(tender)
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    with change_auth(self.app, ("Basic", ("brokerr", ""))):
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": complaint_data,
            },
            status=403,
        )
    self.assertEqual(
        response.json["errors"][0],
        {"location": "body", "name": "data", "description": "Can't add complaint for restricted tender"},
    )
