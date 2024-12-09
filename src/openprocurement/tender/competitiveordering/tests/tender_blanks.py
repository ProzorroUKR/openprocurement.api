from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import TZ, parse_date
from openprocurement.api.utils import get_now
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
    test_tender_below_lots,
)
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.core.utils import calculate_tender_full_date


def patch_tender_period(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.tender_id, self.tender_token = tender["id"], response.json["access"]["token"]

    add_criteria(self)
    self.set_enquiry_period_end()  # sets tenderPeriod.startDate in the past, be careful
    response = self.app.get(f"/tenders/{tender['id']}")
    tender = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], self.tender_token),
        {"data": {"description": "new description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "tenderPeriod should be extended by 3 days")

    tender_period_end_date = (
        calculate_tender_full_date(
            get_now(),
            timedelta(days=7),
            tender=tender,
        )
        + timedelta(seconds=1)
    ).astimezone(TZ)
    enquiry_period_end_date = calculate_tender_full_date(
        tender_period_end_date,
        -timedelta(days=3),
        tender=tender,
    )
    tender_period = deepcopy(tender["tenderPeriod"])
    tender_period["endDate"] = tender_period_end_date.isoformat()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], self.tender_token),
        {"data": {"description": "new description", "tenderPeriod": tender_period}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["tenderPeriod"]["endDate"], tender_period_end_date.isoformat())
    self.assertEqual(response.json["data"]["enquiryPeriod"]["endDate"], enquiry_period_end_date.isoformat())


def patch_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    dateModified = tender.pop("dateModified")

    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "cancelled"}}, status=422
    )

    procuring_entity = deepcopy(tender["procuringEntity"])
    procuring_entity["kind"] = "defense"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": procuring_entity}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "procuringEntity",
                "description": "Can't change procuringEntity.kind in a public tender",
            }
        ],
    )

    tender_period = deepcopy(tender["tenderPeriod"])
    tender_period["startDate"] = tender_period["endDate"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"tenderPeriod": tender_period}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "tenderPeriod",
                "description": ["tenderPeriod must be at least 3 full calendar days long"],
            }
        ],
    )
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procurementMethodRationale": "Open"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("invalidationDate", response.json["data"]["enquiryPeriod"])
    new_tender = response.json["data"]
    new_enquiryPeriod = new_tender.pop("enquiryPeriod")
    new_dateModified = new_tender.pop("dateModified")
    tender.pop("enquiryPeriod")
    tender["procurementMethodRationale"] = "Open"
    self.assertEqual(tender, new_tender)
    self.assertNotEqual(dateModified, new_dateModified)

    revisions = self.mongodb.tenders.get(tender["id"]).get("revisions")
    self.assertTrue(
        any(i for i in revisions[-1]["changes"] if i["op"] == "remove" and i["path"] == "/procurementMethodRationale")
    )

    # update again
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procurementMethodRationale": "OpenOpen"}},
    )
    new_tender2 = response.json["data"]
    new_enquiryPeriod2 = new_tender2.pop("enquiryPeriod")
    new_dateModified2 = new_tender2.pop("dateModified")
    new_tender.pop("procurementMethodRationale")
    new_tender2.pop("procurementMethodRationale")
    self.assertEqual(new_tender, new_tender2)
    self.assertNotEqual(new_enquiryPeriod, new_enquiryPeriod2)
    self.assertNotEqual(new_dateModified, new_dateModified2)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"dateModified": new_dateModified}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "dateModified", "description": "Rogue field"}]
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [self.initial_data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [self.initial_data["items"][0], self.initial_data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    item0 = response.json["data"]["items"][0]
    item1 = response.json["data"]["items"][1]
    self.assertNotEqual(item0.pop("id"), item1.pop("id"))
    self.assertEqual(item0, item1)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [self.initial_data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    item = deepcopy(self.initial_data["items"][0])
    item["classification"] = {"scheme": "ДК021", "id": "44620000-2", "description": "Cartons 2"}
    if self.agreement_id:
        agreement = self.mongodb.agreements.get(self.agreement_id)
        agreement["classification"] = {"scheme": "ДК021", "id": "44620000-2"}
        self.mongodb.agreements.save(agreement)
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
        status=200,
    )

    item["classification"] = {
        "scheme": "ДК021",
        "id": "55523100-3",
        "description": "Послуги з харчування у школах",
    }
    if self.agreement_id:
        agreement = self.mongodb.agreements.get(self.agreement_id)
        agreement["classification"] = {"scheme": "ДК021", "id": "55523100-3"}
        self.mongodb.agreements.save(agreement)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0],
        {"description": ["Can't change classification group of items"], "location": "body", "name": "items"},
    )

    item = deepcopy(self.initial_data["items"][0])
    item["additionalClassifications"] = [tender["items"][0]["additionalClassifications"][0] for i in range(3)]
    if self.agreement_id:
        agreement = self.mongodb.agreements.get(self.agreement_id)
        agreement["classification"] = self.initial_data["items"][0]["classification"]
        self.mongodb.agreements.save(agreement)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    item = deepcopy(self.initial_data["items"][0])
    item["additionalClassifications"] = tender["items"][0]["additionalClassifications"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    period = {
        "startDate": calculate_tender_full_date(
            parse_date(new_dateModified2),
            -timedelta(3),
            tender=None,
            working_days=True,
        ).isoformat(),
        "endDate": new_dateModified2,
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"enquiryPeriod": period}},
    )
    result = response.json["data"]
    self.assertNotEqual(period["startDate"], result["enquiryPeriod"]["startDate"])
    self.assertNotEqual(period["endDate"], result["enquiryPeriod"]["endDate"])
    self.assertEqual(tender["enquiryPeriod"]["startDate"], result["enquiryPeriod"]["startDate"])
    self.assertEqual(tender["enquiryPeriod"]["endDate"], result["enquiryPeriod"]["endDate"])

    # set lots
    base_value = result["value"]
    base_currency, base_tax = base_value["currency"], base_value["valueAddedTaxIncluded"]
    for lot in test_tender_below_lots:
        response = self.app.post_json(f"/tenders/{tender['id']}/lots?acc_token={owner_token}", {"data": lot})
        self.assertEqual(response.status, "201 Created")
        lot_data = response.json["data"]
        self.assertEqual(lot_data["value"]["currency"], base_currency)
        self.assertEqual(lot_data["value"]["valueAddedTaxIncluded"], base_tax)

    changed_value = deepcopy(base_value)
    changed_value["valueAddedTaxIncluded"] = not base_tax
    changed_value["currency"] = "GBP"
    minimal_step = {"amount": result["minimalStep"]["amount"], "currency": "GBP", "valueAddedTaxIncluded": not base_tax}
    response = self.app.patch_json(
        f"/tenders/{tender['id']}?acc_token={owner_token}",
        {
            "data": {
                "value": changed_value,
                "minimalStep": minimal_step,
            }
        },
    )
    result = response.json["data"]
    new_value = result["value"]

    self.assertEqual(changed_value["currency"], new_value["currency"])
    self.assertEqual(changed_value["valueAddedTaxIncluded"], new_value["valueAddedTaxIncluded"])

    for lot in result["lots"]:
        self.assertEqual(lot["value"]["currency"], new_value["currency"])
        self.assertEqual(lot["value"]["valueAddedTaxIncluded"], new_value["valueAddedTaxIncluded"])

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def create_tender_co(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("complaintPeriod", response.json["data"])
    tender_id = response.json["data"]["id"]

    # try to add complaint
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    response = self.app.post_json(f"/tenders/{tender_id}/complaints", {"data": complaint_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint as it is forbidden by configuration"
    )


def create_tender_co_invalid_config(self):
    for config_name in ("hasTenderComplaints", "hasAwardComplaints", "hasCancellationComplaints"):
        config = deepcopy(self.initial_config)
        config.update({config_name: True})
        response = self.app.post_json(
            "/tenders",
            {
                "data": self.initial_data,
                "config": config,
            },
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{"description": "True is not one of [False]", "location": "body", "name": config_name}],
        )


def create_tender_co_invalid_agreement(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"

    config = deepcopy(self.initial_config)
    config.update({"hasPreSelectionAgreement": True})

    response = self.app.post_json(
        "/tenders",
        {
            "data": self.initial_data,
            "config": config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    self.tender_id, self.tender_token = tender_id, owner_token
    add_criteria(self)

    # Invalid agreement type
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["agreementType"] = "invalid"
    self.mongodb.agreements.save(agreement)

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={owner_token}",
        {"data": {"status": "active.tendering"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "agreements", "description": "Agreement type mismatch."}],
    )

    # DPS agreement with hasItems set to True is forbidden
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["agreementType"] = DPS_TYPE
    agreement["hasItems"] = True
    self.mongodb.agreements.save(agreement)

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={owner_token}",
        {"data": {"status": "active.tendering"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "agreements", "description": "Agreement with items is not allowed."}],
    )
