from copy import deepcopy
from datetime import timedelta
from unittest import mock

from openprocurement.api.constants import TZ
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.tests.base import change_auth
from openprocurement.api.utils import get_now
from openprocurement.tender.arma.constants import ARMA_TENDERING_EXTRA_PERIOD
from openprocurement.tender.core.constants import (
    AGREEMENT_CONTRACTS_MESSAGE,
    AGREEMENT_IDENTIFIER_MESSAGE,
    AGREEMENT_NOT_FOUND_MESSAGE,
    AGREEMENT_STATUS_MESSAGE,
)
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.core.tests.utils import activate_contract, set_bid_lotvalues
from openprocurement.tender.core.utils import calculate_tender_full_date
from openprocurement.tender.open.tests.below_threshold.base import test_tender_below_supplier


def create_tender_without_agreement(self):
    data = deepcopy(self.initial_data)
    del data["agreement"]

    response = self.app.post_json(
        "/tenders",
        {"data": data, "config": self.initial_config},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "agreement", "description": ["This field is required."]}],
    )


def create_tender_with_unknown_agreement(self):
    data = deepcopy(self.initial_data)
    data["agreement"] = {"id": "0" * 32}

    response = self.app.post_json(
        "/tenders",
        {"data": data, "config": self.initial_config},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "agreement", "description": AGREEMENT_NOT_FOUND_MESSAGE}],
    )


def create_tender_with_invalid_agreement_type(self):
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["agreementType"] = "electronicCatalogue"
    self.mongodb.agreements.save(agreement)

    response = self.app.post_json(
        "/tenders",
        {"data": self.initial_data, "config": self.initial_config},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "agreement", "description": "Agreement type mismatch."}],
    )


def create_tender_with_mismatched_agreement_procuring_entity(self):
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["procuringEntity"]["identifier"]["id"] = "00000000"
    self.mongodb.agreements.save(agreement)

    response = self.app.post_json(
        "/tenders",
        {"data": self.initial_data, "config": self.initial_config},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "agreement", "description": AGREEMENT_IDENTIFIER_MESSAGE}],
    )


def activate_tender_with_inactive_agreement(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    self.tender_id, self.tender_token = tender_id, owner_token
    add_criteria(self)
    self.add_contract_proforma_doc(tender_id, owner_token)
    self.add_sign_doc(tender_id, owner_token)

    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["status"] = "terminated"
    self.mongodb.agreements.save(agreement)

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={owner_token}",
        {"data": {"status": "active.tendering"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "agreement", "description": AGREEMENT_STATUS_MESSAGE}],
    )


def activate_tender_with_insufficient_agreement_contracts(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    self.tender_id, self.tender_token = tender_id, owner_token
    add_criteria(self)
    self.add_contract_proforma_doc(tender_id, owner_token)
    self.add_sign_doc(tender_id, owner_token)

    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["contracts"][0]["status"] = "terminated"
    self.mongodb.agreements.save(agreement)

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={owner_token}",
        {"data": {"status": "active.tendering"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "agreement", "description": AGREEMENT_CONTRACTS_MESSAGE.format(2)}],
    )


def patch_tender_period(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.tender_id, self.tender_token = tender["id"], response.json["access"]["token"]

    add_criteria(self)
    self.set_enquiry_period_end()
    response = self.app.get(f"/tenders/{tender['id']}")
    tender = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], self.tender_token),
        {"data": {"description": "new description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "tenderPeriod should be extended by {} days".format(ARMA_TENDERING_EXTRA_PERIOD.days),
    )

    tender_period_end_date = (
        calculate_tender_full_date(get_now(), ARMA_TENDERING_EXTRA_PERIOD, tender=tender) + timedelta(seconds=1)
    ).astimezone(TZ)
    tender_period = deepcopy(tender["tenderPeriod"])
    tender_period["endDate"] = tender_period_end_date.isoformat()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], self.tender_token),
        {"data": {"description": "new description", "tenderPeriod": tender_period}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["tenderPeriod"]["endDate"], tender_period_end_date.isoformat())
    self.assertNotIn("enquiryPeriod", response.json["data"])


def patch_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    item_id = tender["items"][0]["id"]
    self.tender_id = tender["id"]
    dateModified = tender.pop("dateModified")

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
                "description": ["tenderPeriod must be at least 10 full business days long"],
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procurementMethodRationale": "Open"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_tender = response.json["data"]
    new_dateModified = new_tender.pop("dateModified")
    tender["procurementMethodRationale"] = "Open"
    self.assertEqual(tender, new_tender)
    self.assertNotEqual(dateModified, new_dateModified)

    revisions = self.mongodb.tenders.get(tender["id"]).get("revisions")
    self.assertTrue(
        any(i for i in revisions[-1]["changes"] if i["op"] == "remove" and i["path"] == "/procurementMethodRationale")
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"dateModified": new_dateModified}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "dateModified", "description": "Rogue field"}]
    )

    item = deepcopy(self.initial_data["items"][0])
    item["id"] = item_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"valueAddedTaxIncluded": True}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0],
        {"description": {"valueAddedTaxIncluded": "Rogue field"}, "location": "body", "name": "guarantee"},
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"amount": 12, "currency": "UAH"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 12)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"status": "active.auction"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def lost_contract_for_active_award(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["tenderers"] = [deepcopy(test_tender_below_supplier)]
    set_bid_lotvalues(bid_data, response.json["data"]["lots"])
    _, bid1_token = self.create_bid(tender_id, bid_data, "pending")
    self.create_bid(tender_id, deepcopy(bid_data), "pending")

    self.set_status("active.auction", {"id": tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for lot in response.json["data"]["lots"]:
        self.app.post_json(
            "/tenders/{}/auction/{}".format(tender_id, lot["id"]),
            {
                "data": {
                    "bids": [
                        {
                            "id": b["id"],
                            "lotValues": [
                                {"relatedLot": lot_value["relatedLot"], "value": lot_value["value"]}
                                for lot_value in b["lotValues"]
                            ],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
        )

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    tender = self.mongodb.tenders.get(tender_id)
    for i in tender["contracts"]:
        self.mongodb.contracts.delete(i["id"])
    del tender["contracts"]
    self.mongodb.tenders.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.assertIn("contracts", response.json["data"])
    self.assertNotIn("next_check", response.json["data"])
    contract_id = response.json["data"]["contracts"][-1]["id"]

    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid1_token)

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def create_tender_generated(self):
    data = self.initial_data.copy()
    data.update({"id": "hash"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    if "procurementMethodDetails" in tender:
        tender.pop("procurementMethodDetails")
    self.assertEqual(
        set(tender),
        {
            "agreement",
            "awardCriteria",
            "contractChangeRationaleTypes",
            "criteria",
            "date",
            "dateCreated",
            "dateModified",
            "documents",
            "id",
            "items",
            "lots",
            "mainProcurementCategory",
            "next_check",
            "noticePublicationDate",
            "owner",
            "procurementMethod",
            "procurementMethodType",
            "procuringEntity",
            "status",
            "submissionMethod",
            "tenderID",
            "tenderPeriod",
            "title",
            "title_en",
        },
    )
    self.assertNotEqual(data["id"], tender["id"])
    self.assertEqual(tender["agreement"]["id"], self.agreement_id)


def patch_tender_draft(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    tender_period = tender["tenderPeriod"]
    tender_period["startDate"] = (parse_date(tender_period["startDate"]) + timedelta(days=1)).isoformat()
    tender_period["endDate"] = (parse_date(tender_period["endDate"]) + timedelta(days=1)).isoformat()

    item = deepcopy(tender["items"][0])
    item.update(description="test item", quantity=20, id="0" * 32)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"items": [item], "tenderPeriod": tender_period}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(len(tender["items"]), 1)
    self.assertEqual(tender["items"][0]["description"], "test item")
    self.assertEqual(tender["tenderPeriod"], tender_period)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "features": [
                    {
                        "title": "test feature",
                        "relatedItem": "0" * 32,
                        "featureOf": "item",
                        "enum": [{"value": 0.1, "title": "test feature value"}],
                    }
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["features"][0]["title"], "test feature")


def one_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    self.set_initial_status(response.json)

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["tenderers"] = [deepcopy(test_tender_below_supplier)]
    set_bid_lotvalues(bid_data, response.json["data"]["lots"])
    self.create_bid(tender_id, bid_data, "pending")

    self.set_status("active.auction", {"id": tender_id, "status": "active.tendering"})
    self.check_chronograph()

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def first_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["tenderers"] = [deepcopy(test_tender_below_supplier)]
    set_bid_lotvalues(bid_data, response.json["data"]["lots"])
    _, bid1_token = self.create_bid(tender_id, bid_data, "pending")
    self.create_bid(tender_id, deepcopy(bid_data), "pending")

    self.set_status("active.auction", {"id": tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for lot in response.json["data"]["lots"]:
        response = self.app.post_json(
            "/tenders/{}/auction/{}".format(tender_id, lot["id"]),
            {
                "data": {
                    "bids": [
                        {
                            "id": b["id"],
                            "lotValues": [
                                {"relatedLot": lot_value["relatedLot"], "value": lot_value["value"]}
                                for lot_value in b["lotValues"]
                            ],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
        )
        self.assertEqual(response.status, "200 OK")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}".format(tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]
    activate_contract(self, tender_id, contract_id, owner_token, bid1_token)

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


@mock.patch(
    "openprocurement.tender.arma.procedure.state.tender_details.ARMA_MIN_EXPECTED_INCOME_FROM",
    get_now() - timedelta(days=1),
)
def patch_tender_lot_min_expected_income(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"
    for lot in data["lots"]:
        lot.pop("minExpectedIncome", None)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    token = response.json["access"]["token"]
    lot_id = response.json["data"]["lots"][0]["id"]

    self.assertNotIn("minExpectedIncome", response.json["data"])
    self.assertNotIn("minExpectedIncome", response.json["data"]["lots"][0])

    # minExpectedIncome is not a tender level field anymore
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"minExpectedIncome": {"amount": 100000.00, "currency": "UAH", "valueAddedTaxIncluded": True}}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "minExpectedIncome", "description": "Rogue field"}],
    )

    response = self.app.patch_json(
        f"/tenders/{tender_id}/lots/{lot_id}?acc_token={token}",
        {"data": {"minExpectedIncome": {"amount": 100000.00, "currency": "UAH"}}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "minExpectedIncome",
                "description": {"valueAddedTaxIncluded": ["This field is required."]},
            }
        ],
    )

    response = self.app.patch_json(
        f"/tenders/{tender_id}/lots/{lot_id}?acc_token={token}",
        {"data": {"minExpectedIncome": {"amount": 100000.00, "currency": "USD", "valueAddedTaxIncluded": True}}},
        status=422,
    )
    self.assertEqual(response.json["errors"][0]["name"], "minExpectedIncome")

    response = self.app.patch_json(
        f"/tenders/{tender_id}/lots/{lot_id}?acc_token={token}",
        {"data": {"minExpectedIncome": {"amount": -1, "currency": "UAH", "valueAddedTaxIncluded": True}}},
        status=422,
    )
    self.assertEqual(response.json["errors"][0]["name"], "minExpectedIncome")

    response = self.app.patch_json(
        f"/tenders/{tender_id}/lots/{lot_id}?acc_token={token}",
        {"data": {"minExpectedIncome": {"amount": 100000.00, "currency": "UAH", "valueAddedTaxIncluded": True}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        response.json["data"]["minExpectedIncome"],
        {"amount": 100000.0, "currency": "UAH", "valueAddedTaxIncluded": True},
    )

    data_no_income = deepcopy(self.initial_data)
    data_no_income["status"] = "draft"
    for lot in data_no_income["lots"]:
        lot.pop("minExpectedIncome", None)
    response = self.app.post_json("/tenders", {"data": data_no_income, "config": self.initial_config})
    tender_id2 = response.json["data"]["id"]
    token2 = response.json["access"]["token"]

    add_criteria(self, tender_id2, token2)
    self.app.post_json(
        f"/tenders/{tender_id2}/documents?acc_token={token2}",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentType": "contractProforma",
            }
        },
    )
    self.add_sign_doc(tender_id2, token2)

    response = self.app.patch_json(
        f"/tenders/{tender_id2}?acc_token={token2}",
        {"data": {"status": "active.tendering"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertIn(
        {
            "location": "body",
            "name": "minExpectedIncome",
            "description": "minExpectedIncome is required for tender activation",
        },
        response.json["errors"],
    )

    response = self.set_initial_status({"data": {"id": tender_id}, "access": {"token": token}})
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertEqual(
        response.json["data"]["lots"][0]["minExpectedIncome"],
        {"amount": 100000.0, "currency": "UAH", "valueAddedTaxIncluded": True},
    )

    response = self.app.patch_json(
        f"/tenders/{tender_id}/lots/{lot_id}?acc_token={token}",
        {"data": {"minExpectedIncome": {"amount": 200000.00, "currency": "UAH", "valueAddedTaxIncluded": False}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        response.json["data"]["minExpectedIncome"],
        {"amount": 200000.0, "currency": "UAH", "valueAddedTaxIncluded": False},
    )

    response = self.app.patch_json(
        f"/tenders/{tender_id}/lots/{lot_id}?acc_token={token}",
        {"data": {"minExpectedIncome": {"amount": 100000.999, "currency": "UAH", "valueAddedTaxIncluded": True}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        response.json["data"]["minExpectedIncome"],
        {"amount": 100001.0, "currency": "UAH", "valueAddedTaxIncluded": True},
    )

    # None removes the field, which is not allowed after draft
    response = self.app.patch_json(
        f"/tenders/{tender_id}/lots/{lot_id}?acc_token={token}",
        {"data": {"minExpectedIncome": None}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "minExpectedIncome", "description": "minExpectedIncome is required for lot"}],
    )

    response = self.app.get(f"/tenders/{tender_id}")
    self.assertEqual(
        response.json["data"]["lots"][0]["minExpectedIncome"],
        {"amount": 100001.0, "currency": "UAH", "valueAddedTaxIncluded": True},
    )

    with change_auth(self.app, ("Basic", ("administrator", ""))):
        response = self.app.get(f"/tenders/{tender_id}/billing")
    self.assertNotIn("minExpectedIncome", response.json["data"])
    self.assertEqual(
        response.json["data"]["lots"][0]["minExpectedIncome"],
        {"amount": 100001.0, "currency": "UAH", "valueAddedTaxIncluded": True},
    )

    self.tender_id = tender_id
    self.set_status("active.auction")
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {
            "data": {
                "lots": [
                    {
                        "id": lot_id,
                        "title": "lot title",
                        "minExpectedIncome": {
                            "amount": 300000.00,
                            "currency": "UAH",
                            "valueAddedTaxIncluded": True,
                        },
                    }
                ]
            }
        },
        status=403,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update tender in current (active.auction) status",
    )
