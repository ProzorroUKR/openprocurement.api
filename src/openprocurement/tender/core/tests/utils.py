import unittest
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta
from unittest.mock import MagicMock, call, patch
from uuid import uuid4

from pyramid.exceptions import URLDecodeError

from openprocurement.api.constants import TZ
from openprocurement.api.context import set_now
from openprocurement.api.procedure.utils import parse_date
from openprocurement.tender.core.procedure.utils import (
    extract_tender_doc,
    extract_tender_id,
    generate_tender_id,
)
from openprocurement.tender.core.utils import calculate_tender_full_date


class TestUtilsBase(unittest.TestCase):
    def setUp(self):
        self.tender_data = {
            "id": "ae50ea25bb1349898600ab380ee74e57",
            "dateModified": "2016-04-18T11:26:10.320970+03:00",
            "status": "draft",
            "tenderID": "UA-2016-04-18-000003",
        }
        self.lots = [
            {
                "id": "11111111111111111111111111111111",
                "title": "Earth",
                "value": {"amount": 500000},
                "minimalStep": {"amount": 1000},
            },
            {
                "id": "22222222222222222222222222222222",
                "title": "Mars",
                "value": {"amount": 600000},
                "minimalStep": {"amount": 2000},
            },
        ]
        self.items = [{"description": "Some item", "relatedLot": "11111111111111111111111111111111"}]


class TestUtils(TestUtilsBase):
    def setUp(self):
        self.tender_data = {
            "id": "ae50ea25bb1349898600ab380ee74e57",
            "dateModified": "2016-04-18T11:26:10.320970+03:00",
            "status": "draft",
            "tenderID": "UA-2016-04-18-000003",
        }
        self.lots = [
            {
                "id": "11111111111111111111111111111111",
                "title": "Earth",
                "value": {"amount": 500000},
                "minimalStep": {"amount": 1000},
            },
            {
                "id": "22222222222222222222222222222222",
                "title": "Mars",
                "value": {"amount": 600000},
                "minimalStep": {"amount": 2000},
            },
        ]
        self.items = [{"description": "Some item", "relatedLot": "11111111111111111111111111111111"}]

    def test_generate_tender_id(self):
        set_now()
        ctime = datetime.now(TZ)
        request = MagicMock()
        request.registry.mongodb.get_next_sequence_value.return_value = 99

        tender_id = generate_tender_id(request)
        tid = "UA-{:04}-{:02}-{:02}-{:06}-a".format(ctime.year, ctime.month, ctime.day, 99)
        self.assertEqual(tid, tender_id)

    @patch("openprocurement.tender.core.procedure.utils.decode_path_info")
    @patch("openprocurement.tender.core.procedure.utils.error_handler")
    def test_extract_tender_id(self, mocked_error_handler, mocked_decode_path):
        mocked_error_handler.return_value = Exception("Oops.")
        mocked_decode_path.side_effect = [
            KeyError("Missing 'PATH_INFO'"),
            UnicodeDecodeError("UTF-8", b"obj", 1, 10, "Hm..."),
            "/",
            "/api/2.3/tenders/{}".format(self.tender_data["id"]),
        ]
        request = MagicMock()
        request.environ = {"PATH_INFO": "/"}

        # Test with KeyError
        self.assertIs(extract_tender_id(request), None)

        # Test with UnicodeDecodeError
        with self.assertRaises(URLDecodeError) as e:
            extract_tender_id(request)
        self.assertEqual(e.exception.encoding, "UTF-8")
        self.assertEqual(e.exception.object, b"obj")
        self.assertEqual(e.exception.start, 1)
        self.assertEqual(e.exception.end, 10)
        self.assertEqual(e.exception.reason, "Hm...")
        self.assertIsInstance(e.exception, URLDecodeError)

        # Test with path '/'
        self.assertIs(extract_tender_id(request), None)

    @patch("openprocurement.tender.core.procedure.utils.extract_tender_id")
    def test_extract_tender_doc(self, mocked_extract_tender_id):
        tender_data = deepcopy(self.tender_data)
        mocked_extract_tender_id.return_value = tender_data["id"]
        tender_data["doc_type"] = "Tender"
        request = MagicMock()
        request.registry.db = MagicMock()

        # Test with extract_tender_adapter raise HTTP 404
        request.registry.mongodb.tenders.get.return_value = None
        with self.assertRaises(Exception):
            extract_tender_doc(request)
        self.assertEqual(request.errors.status, 404)
        request.errors.add.assert_has_calls([call("url", "tender_id", "Not Found")])

        # Test with extract_tender_adapter return Tender object
        request.registry.mongodb.tenders.get.return_value = tender_data
        doc = extract_tender_doc(request)
        self.assertEqual(doc, tender_data)


class TestCalculateTenderBusinessDate(TestUtilsBase):
    def test_working_days(self):
        date_obj = parse_date("2020-11-07T12:00:00+02:00")
        delta_obj = timedelta(days=7)

        business_date = calculate_tender_full_date(date_obj, delta_obj, tender={}, working_days=True)
        self.assertEqual(business_date.isoformat(), "2020-11-18T00:00:00+02:00")

    def test_working_days_backwards(self):
        date_obj = parse_date("2020-11-19T12:00:00+02:00")
        delta_obj = -timedelta(days=7)

        business_date = calculate_tender_full_date(date_obj, delta_obj, tender={}, working_days=True)
        self.assertEqual(business_date.isoformat(), "2020-11-10T00:00:00+02:00")

    def test_calendar_days(self):
        date_obj = parse_date("2020-11-07T12:00:00+02:00")
        delta_obj = timedelta(days=7)

        business_date = calculate_tender_full_date(date_obj, delta_obj, tender={}, working_days=False)
        self.assertEqual(business_date.isoformat(), "2020-11-15T00:00:00+02:00")

    def test_calendar_days_backwards(self):
        date_obj = parse_date("2020-11-15T12:00:00+02:00")
        delta_obj = -timedelta(days=7)

        business_date = calculate_tender_full_date(date_obj, delta_obj, tender={}, working_days=False)
        self.assertEqual(business_date.isoformat(), "2020-11-08T00:00:00+02:00")

    def test_working_days_dst_transition(self):
        date_obj = parse_date("2021-03-10T12:00:00+02:00")
        delta_obj = timedelta(days=30)

        business_date = calculate_tender_full_date(date_obj, delta_obj, tender={}, working_days=True)
        self.assertEqual(business_date.isoformat(), "2021-04-22T00:00:00+03:00")

    def test_working_days_dst_transition_backwards(self):
        date_obj = parse_date("2021-04-21T12:00:00+03:00")
        delta_obj = -timedelta(days=30)

        business_date = calculate_tender_full_date(date_obj, delta_obj, tender={}, working_days=True)
        self.assertEqual(business_date.isoformat(), "2021-03-10T00:00:00+02:00")

    def test_calendar_dst_transition(self):
        date_obj = parse_date("2021-03-10T12:00:00+02:00")
        delta_obj = timedelta(days=30)

        business_date = calculate_tender_full_date(date_obj, delta_obj, tender={}, working_days=False)
        self.assertEqual(business_date.isoformat(), "2021-04-10T00:00:00+03:00")

    def test_calendar_dst_transition_backwards(self):
        date_obj = parse_date("2021-04-10T12:00:00+03:00")
        delta_obj = -timedelta(days=30)

        business_date = calculate_tender_full_date(date_obj, delta_obj, tender={}, working_days=False)
        self.assertEqual(business_date.isoformat(), "2021-03-11T00:00:00+02:00")

    def test_calendar_dst_transition_backwards_from_midnight(self):
        date_obj = parse_date("2021-04-10T00:00:00+03:00")
        delta_obj = -timedelta(days=30)

        business_date = calculate_tender_full_date(date_obj, delta_obj, tender={}, working_days=False)
        self.assertEqual(business_date.isoformat(), "2021-03-11T00:00:00+02:00")

    def test_with_accelerator(self):
        date_obj = datetime(2021, 10, 7)
        delta_obj = timedelta(days=7)

        # Test with accelerator = 1440
        context = {"procurementMethodDetails": "quick, accelerator=1440", "procurementMethodType": "negotiation"}
        business_date = calculate_tender_full_date(date_obj, delta_obj, tender=context, working_days=True)
        self.assertEqual(business_date, datetime(2021, 10, 7, 0, 7))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestUtils))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")


@contextmanager
def change_auth(app, auth):
    authorization = app.authorization
    app.authorization = auth
    yield app
    app.authorization = authorization


def set_tender_lots(tender, lots):
    tender["lots"] = []
    for lot in lots:
        lot = deepcopy(lot)
        lot["id"] = uuid4().hex
        tender["lots"].append(lot)
    for i, item in enumerate(tender["items"]):
        item["relatedLot"] = tender["lots"][i % len(tender["lots"])]["id"]
    for i, milestone in enumerate(tender.get("milestones", [])):
        milestone["relatedLot"] = tender["lots"][0]["id"]
    return tender


def set_tender_criteria(criteria, lots, items):
    for i, criterion in enumerate(criteria):
        if lots and criterion["relatesTo"] == "lot":
            criterion["relatedItem"] = lots[i % len(lots)]["id"]
        elif items and criterion["relatesTo"] == "item":
            criterion["relatedItem"] = items[i % len(lots)]["id"]
    return criteria


def set_bid_items(self, bid, items=None, tender_id=None):
    if not tender_id:
        tender_id = self.tender_id

    response = self.app.get(f"/tenders/{tender_id}")
    tender = response.json["data"]
    if not items:
        items = tender["items"]

    valueAddedTaxIncluded = None
    if bid_value := bid.get("value", {}):
        valueAddedTaxIncluded = bid_value.get("valueAddedTaxIncluded")
    bid_items = []
    related_lot_ids = {lot_value["relatedLot"] for lot_value in bid.get("lotValues") or []}
    for item in items:
        if "relatedLot" in item and item["relatedLot"] not in related_lot_ids:
            continue
        bid_items.append(
            {
                "quantity": 4.0,
                "description": "футляри до державних нагород",
                "id": item['id'],
                "unit": {
                    "name": "Item",
                    "code": "KGM",
                    "value": {"amount": 10.0, "currency": "UAH", "valueAddedTaxIncluded": valueAddedTaxIncluded},
                },
            }
        )
    if bid_items:
        bid["items"] = bid_items
    return bid


def set_bid_responses(criteria):
    rrs = []
    for criterion in criteria:
        for req in criterion["requirementGroups"][0]["requirements"]:
            if criterion["source"] in ("tenderer", "winner"):
                rrs.append(
                    {
                        "requirement": {
                            "id": req["id"],
                        },
                        "value": True,
                    },
                )
    return rrs


def set_bid_lotvalues(bid, lots):
    try:
        value = bid.pop("value", None) or bid["lotValues"][0]["value"]
    except KeyError:
        bid["lotValues"] = [{"relatedLot": lot["id"]} for lot in lots]
    else:
        bid["lotValues"] = [{"value": value, "relatedLot": lot["id"]} for lot in lots]
    return bid


def set_tender_multi_buyers(_test_tender_data, _test_item, _test_organization):
    _tender_data = deepcopy(_test_tender_data)

    # create 3 items
    test_item1 = deepcopy(_test_item)
    test_item1["description"] = "телевізори"

    test_item2 = deepcopy(_test_item)
    test_item2["description"] = "портфелі"
    test_item2.pop("id", None)

    test_item3 = deepcopy(_test_item)
    test_item3["description"] = "столи"
    test_item3.pop("id", None)

    _tender_data["items"] = [test_item1, test_item2, test_item2]

    # create 2 buyers
    buyer1_id = uuid4().hex
    buyer2_id = uuid4().hex

    _test_organization_1 = deepcopy(_test_organization)
    _test_organization_2 = deepcopy(_test_organization)
    _test_organization_2["identifier"]["id"] = "00037254"

    _tender_data["buyers"] = [
        {"id": buyer1_id, "name": _test_organization_1["name"], "identifier": _test_organization_1["identifier"]},
        {"id": buyer2_id, "name": _test_organization_2["name"], "identifier": _test_organization_2["identifier"]},
    ]
    # assign items to buyers
    _tender_data["items"][0]["relatedBuyer"] = buyer1_id
    _tender_data["items"][1]["relatedBuyer"] = buyer2_id
    _tender_data["items"][2]["relatedBuyer"] = buyer2_id

    return _tender_data


def get_contract_data(self, tender_id):
    response = self.app.get(f"/tenders/{tender_id}")
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    response = self.app.get(f"/contracts/{contract_id}")
    contract = response.json["data"]

    return contract


def patch_contract(self, tender_id, tender_token, contract_id, data):
    self.app.patch_json(
        f"/tenders/{tender_id}/contracts/{contract_id}?acc_token={tender_token}",
        {"data": data},
    )
    # self.app.patch_json(f"/contracts/{contract_id}?acc_token={tender_token}", {"data": {}})
    #
    # self.app.patch_json(
    #     f"/contracts/{contract_id}?acc_token={tender_token}",
    #     {"data": data},
    # )


def activate_contract(self, tender_id, contract_id, tender_token, bid_token):
    response = self.app.get(f"/tenders/{tender_id}")
    tender_type = response.json["data"]["procurementMethodType"]
    test_signer_info = {
        "name": "Test Testovich",
        "telephone": "+380950000000",
        "email": "example@email.com",
        "iban": "1" * 15,
        "authorizedBy": "статут",
        "position": "Генеральний директор",
    }
    response = self.app.put_json(
        f"/contracts/{contract_id}/suppliers/signer_info?acc_token={bid_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{contract_id}/buyer/signer_info?acc_token={tender_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={tender_token}",
        {
            "data": {
                "status": "active",
                "contractNumber": "123",
                "period": {
                    "startDate": "2023-03-18T18:47:47.155143+02:00",
                    "endDate": "2023-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    return response.json["data"]
