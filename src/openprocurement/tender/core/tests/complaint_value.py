# -*- coding: utf-8 -*-
from openprocurement.api.tests.base import singleton_app, app
from openprocurement.tender.belowthreshold.tests.base import test_author, test_draft_complaint, test_lots
from openprocurement.tender.openua.tests.base import test_tender_data
from openprocurement.tender.core.utils import round_up_to_ten
from openprocurement.tender.core.models import Complaint, Award
from openprocurement.tender.core.constants import (
    COMPLAINT_MIN_AMOUNT, COMPLAINT_MAX_AMOUNT, COMPLAINT_ENHANCED_AMOUNT_RATE,
    COMPLAINT_ENHANCED_MIN_AMOUNT, COMPLAINT_ENHANCED_MAX_AMOUNT
)
from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from copy import deepcopy
from mock import patch, Mock
from datetime import datetime, timedelta
import pytest
import pytz

test_tender_data = deepcopy(test_tender_data)
complaint_data = deepcopy(test_draft_complaint)


def create_tender(app, tender_data):
    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/tenders", dict(data=tender_data))
    assert response.status == "201 Created"
    return response.json


def test_complaint_value_change(app):
    """
    value should be calculated only once for a complaint
    """
    test_tender_data["value"]["amount"] = 1000  # we want minimum complaint value
    tender = create_tender(app, test_tender_data)
    with patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1)):
        response = app.post_json(
            "/tenders/{}/complaints".format(tender["data"]["id"]),
            {"data": complaint_data},
        )
    response_data = response.json["data"]
    assert "value" in response_data
    expected_value = {"currency": "UAH", "amount": COMPLAINT_MIN_AMOUNT}
    assert response_data["value"] == expected_value

    # if we deploy new constant values the value shouldn't change
    with patch("openprocurement.tender.core.models.COMPLAINT_MIN_AMOUNT", 40):
        response = app.get("/tenders/{}".format(tender["data"]["id"]))
        complaint = response.json["data"].get("complaints")[0]
        assert complaint["value"] == expected_value


def test_complaint_value_with_lots(app):
    """
    Value should be based on a lot value if lots are present
    """
    test_data = deepcopy(test_tender_data)
    test_data["lots"] = deepcopy(test_lots)
    test_data["lots"].append(deepcopy(test_lots[0]))
    test_data["lots"][0]["value"]["amount"] = 500
    test_data["lots"][1]["value"]["amount"] = 99999999999999
    tender = create_tender(app, test_data)

    req_data = deepcopy(complaint_data)
    # a chip complaint
    req_data["relatedLot"] = tender["data"]["lots"][0]["id"]

    with patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1)):
        response = app.post_json(
            "/tenders/{}/complaints".format(tender["data"]["id"]),
            {"data": req_data},
        )

    response_data = response.json["data"]
    assert "value" in response_data
    assert response_data["value"] == {"currency": "UAH", "amount": COMPLAINT_MIN_AMOUNT}

    # an expensive one
    req_data["relatedLot"] = tender["data"]["lots"][1]["id"]
    with patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1)):
        response = app.post_json(
            "/tenders/{}/complaints".format(tender["data"]["id"]),
            {"data": req_data},
        )
    response_data = response.json["data"]
    assert "value" in response_data
    assert response_data["value"] == {"currency": "UAH", "amount": COMPLAINT_MAX_AMOUNT}


def test_award_lot_complaint_rate():
    root = Mock(__parent__=None)
    lot_id = "1" * 32
    root.request.validated = {
        "tender": {
            "revisions": [Mock(date=RELEASE_2020_04_19 + timedelta(days=1))],
            "status": "active.tendering",
            "procurementMethodType": "",
            "value": {
                "amount": 99999999999,
                "currency": "UAH",
            },
            "lots": [
                {
                    "id": lot_id,
                    "value": {
                        "amount": 1000,
                        "currency": "UAH"
                    }
                }
            ]
        },
    }
    award = Award(dict(id="0" * 32, lotID=lot_id))
    award["__parent__"] = root
    complaint = Complaint(complaint_data)
    complaint["__parent__"] = award
    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": COMPLAINT_MIN_AMOUNT}


def test_post_pending_complaint():
    """
    only draft complaints have value
    """
    complaint = Complaint(
        {
            "title": "complaint title",
            "status": "pending",
            "description": "complaint description",
            "author": test_author
        }
    )
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "status": "active.tendering",
        "procurementMethodType": "anything but esco",
        "value": {"amount": 1000}
    }}
    complaint["__parent__"] = root
    result = complaint.serialize()
    assert "value" not in result


def test_post_draft_claim():
    """
    claims don't have value
    """
    complaint = Complaint(
        {
            "title": "complaint title",
            "status": "draft",
            "description": "complaint description",
            "author": test_author
        }
    )
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "status": "active.tendering",
        "procurementMethodType": "anything but esco",
        "value": {"amount": 1000}
    }}
    complaint["__parent__"] = root
    result = complaint.serialize()
    assert "value" not in result


def test_post_not_uah_complaint():
    """
    applying currency rates
    """
    complaint = Complaint(
        {
            "title": "complaint title",
            "status": "draft",
            "type": "complaint",
            "description": "complaint description",
            "author": test_author
        }
    )
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "revisions": [Mock(date=RELEASE_2020_04_19 + timedelta(days=1))],
        "status": "active.tendering",
        "procurementMethodType": "anything but esco",
        "value": {"amount": 30001, "currency": "EUR"}
    }}
    root.request.currency_rates = [
        {
            "cc": "USD",
            "rate": 8.0
        },
        {
            "cc": "EUR",
            "rate": 30.0
        }
    ]
    complaint["__parent__"] = root
    result = complaint.serialize()
    assert "value" in result
    # 30001 * 30 = 900030
    # 900030 * 0.3 / 100 = 2700.09 => 2710
    assert result["value"] == {'currency': 'UAH', 'amount': 2710}


def test_post_not_uah_complaint_esco():
    """
    Esco with currency rates
    """
    complaint = Complaint(
        {
            "title": "complaint title",
            "status": "draft",
            "type": "complaint",
            "description": "complaint description",
            "author": test_author
        }
    )
    root = Mock(__parent__=None)
    root.request.validated = {
        "tender": {
            "revisions": [Mock(date=RELEASE_2020_04_19 + timedelta(days=1))],
            "status": "awarding",
            "procurementMethodType": "esco",
            "bids": [
                {
                    "owner_token": "122344",
                    "value": {"amount": -1, "currency": "UAH"}
                },
                {
                    "owner_token": "secret_stuff",
                    "value": {"amount": 70002, "currency": "USD"},
                }
            ]
        },
    }
    root.request.params = {"acc_token": "secret_stuff"}
    root.request.currency_rates = [
        {
            "cc": "USD",
            "rate": 8.0
        },
        {
            "cc": "EUR",
            "rate": 12.0
        }
    ]
    complaint["__parent__"] = root
    result = complaint.serialize()
    assert "value" in result
    # Converting 70002 USD into 560016.0 UAH using rate 8.0
    # 560016.0 * 0.6/100 = 3360.096 => 3370
    assert result["value"] == {'currency': 'UAH', 'amount': 3370}


@pytest.mark.parametrize("test_data", [
    (1000, COMPLAINT_MIN_AMOUNT),
    (999999999999, COMPLAINT_MAX_AMOUNT),
    (901000, 2710),  # 901000 * 0.3 / 100 = 2703.0 => 2710
])
def test_complaint_non_esco_tendering_rates(test_data):
    tender_amount, expected_complaint_amount = test_data
    complaint = Complaint(complaint_data)
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "revisions": [Mock(date=RELEASE_2020_04_19 + timedelta(days=1))],
        "status": "active.tendering",
        "procurementMethodType": "anything but esco",
        "value": {
            "amount": tender_amount,
            "currency": "UAH"
        }
    }}
    complaint["__parent__"] = root

    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": expected_complaint_amount}


@pytest.mark.parametrize("test_data", [
    (1000, COMPLAINT_ENHANCED_MIN_AMOUNT),
    (999999999999, COMPLAINT_ENHANCED_MAX_AMOUNT),
    (901000, 5410),  # 901000 * 0.6 / 100 = 5406.0 => 5410
])
def test_non_esco_enhanced_rates(test_data):
    tender_amount, expected_complaint_amount = test_data

    complaint = Complaint(complaint_data)
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "revisions": [Mock(date=RELEASE_2020_04_19 + timedelta(days=1))],
        "status": "active.qualification",
        "procurementMethodType": "anything but esco",
        "value": {
            "amount": tender_amount,
            "currency": "UAH"
        }
    }}
    complaint["__parent__"] = root

    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": expected_complaint_amount}


@pytest.mark.parametrize("status", ["active.tendering", "active.pre-qualification",
                                    "active.pre-qualification.stand-still"])
def test_esco_tendering(status):
    complaint = Complaint(complaint_data)
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "revisions": [Mock(date=RELEASE_2020_04_19 + timedelta(days=1))],
        "status": status,
        "procurementMethodType": "esco"
    }}
    complaint["__parent__"] = root

    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": COMPLAINT_MIN_AMOUNT}


@pytest.mark.parametrize("test_data", [
    (1000, COMPLAINT_ENHANCED_MIN_AMOUNT),
    (999999999999, COMPLAINT_ENHANCED_MAX_AMOUNT),
    (901000, 5410),  # 901000 * 0.6 / 100 = 5406.0 => 5410
])
def test_esco_not_tendering_rates(test_data):
    base_amount, expected_complaint_amount = test_data
    complaint = Complaint(complaint_data)
    root = Mock(__parent__=None)
    root.request.validated = {
        "tender": {
            "revisions": [Mock(date=RELEASE_2020_04_19 + timedelta(days=1))],
            "status": "any but tendering and pre-qualification statuses",
            "procurementMethodType": "esco",
            "bids": [
                {
                    "owner_token": "122344",
                    "value": {
                        "amount": -1,
                        "currency": "UAH"
                    }
                },
                {
                    "owner_token": "secret_stuff",
                    "value": {
                        "amount": base_amount,
                        "currency": "UAH"
                    }
                }
            ]
        },
    }
    root.request.params = {"acc_token": "secret_stuff"}
    complaint["__parent__"] = root
    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": expected_complaint_amount}


def test_esco_not_tendering_with_lot():
    amount, expected_amount = 901000, 5410
    complaint = Complaint(complaint_data)

    class MyMock(Mock):
        def get(self, key):
            return getattr(self, key)
    root = Mock(__parent__=None)
    cancellation = MyMock(__parent__=root, relatedLot="lot1", lotID=None)
    root.request.params = {"acc_token": "secret_stuff"}
    root.request.logging_context.items.return_value = ""
    root.request.validated = {"tender": {
        "revisions": [Mock(date=RELEASE_2020_04_19 + timedelta(days=1))],
        "status": "active.qualification",
        "procurementMethodType": "esco",
        "bids": [
            {
                "owner_token": "secret_stuff",
                "lotValues": [
                    {
                        "relatedLot": "lot1",
                        "value": {
                            "amount": amount,
                            "currency": "UAH"
                        }
                    }
                ],
                "tenderers": [{
                    "identifier": {
                        "scheme": "spam",
                        "id": "ham",
                    }
                }]
            },
        ],
        "lots": [
            {"id": "lot1"}
        ]
    }}
    complaint["__parent__"] = cancellation

    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": expected_amount}


def test_lot_esco_non_lot_complaint():
    amount = 901000
    expected_amount = round_up_to_ten(amount * 3 * COMPLAINT_ENHANCED_AMOUNT_RATE)
    complaint = Complaint(complaint_data)

    class MyMock(Mock):
        def get(self, key):
            return getattr(self, key)
    root = Mock(__parent__=None)
    cancellation = MyMock(__parent__=root, relatedLot=None, lotID=None)  # tender cancellation
    root.request.params = {"acc_token": "secret_stuff"}
    root.request.logging_context.items.return_value = ""
    root.request.validated = {"tender": {
        "revisions": [Mock(date=RELEASE_2020_04_19 + timedelta(days=1))],
        "status": "active.qualification",
        "procurementMethodType": "esco",
        "bids": [
            {
                "owner_token": "secret_stuff",
                "lotValues": [
                    {
                        "relatedLot": "lot1",
                        "value": {
                            "amount": amount,  # will be included
                            "currency": "UAH"
                        }
                    },
                    {
                        "relatedLot": "lot2",
                        "value": {
                            "amount": amount,  # will be included
                            "currency": "UAH"
                        }
                    }
                ],
                "tenderers": [{
                    "identifier": {
                        "scheme": "spam",
                        "id": "ham",
                    }
                }]
            },
            {
                "owner_token": "another_secret_stuff",
                "lotValues": [
                    {
                        "relatedLot": "lot1",
                        "value": {
                            "amount": amount,
                            "currency": "UAH"
                        }
                    },
                ],
                "tenderers": [{
                    "identifier": {
                        "scheme": "spam",
                        "id": "pork",
                    }
                }]
            },
            {
                "owner_token": "1232",
                "lotValues": [
                    {
                        "relatedLot": "lot4",
                        "value": {
                            "amount": amount,  # will be included
                            "currency": "UAH"
                        }
                    },
                ],
                "tenderers": [{
                    "identifier": {
                        "scheme": "spam",
                        "id": "ham",
                    }
                }]
            }
        ],
        "lots": [
            {"id": "lot1"}
        ]
    }}
    complaint["__parent__"] = cancellation

    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": expected_amount}


def test_esco_lot_not_related_bidder():
    amount = 901000
    complaint = Complaint(complaint_data)

    class MyMock(Mock):
        def get(self, key):
            return getattr(self, key)
    root = Mock(__parent__=None)
    cancellation = MyMock(__parent__=root, relatedLot="lot999", lotID=None)
    root.request.params = {"acc_token": "secret_stuff"}
    root.request.logging_context.items.return_value = ""
    root.request.validated = {"tender": {
        "revisions": [Mock(date=RELEASE_2020_04_19 + timedelta(days=1))],
        "status": "active.qualification",
        "procurementMethodType": "esco",
        "bids": [
            {
                "owner_token": "secret_stuff",
                "lotValues": [
                    {
                        "relatedLot": "lot1",
                        "value": {
                            "amount": amount,  # included
                            "currency": "UAH"
                        }
                    }
                ],
                "tenderers": [{
                    "identifier": {
                        "scheme": "spam",
                        "id": "ham",
                    }
                }]
            },
            {
                "owner_token": "secret_stuff",
                "lotValues": [
                    {
                        "relatedLot": "lot1",
                        "value": {
                            "amount": amount,
                            "currency": "UAH"
                        }
                    }
                ],
                "tenderers": [{
                    "identifier": {
                        "scheme": "spam",
                        "id": "pork",
                    }
                }]
            },
            {
                "owner_token": "secret_stuff_2",
                "lotValues": [
                    {
                        "relatedLot": "lot2",
                        "value": {
                            "amount": amount,  # included
                            "currency": "UAH"
                        }
                    },
                    {
                        "relatedLot": "lot3",
                        "value": {
                            "amount": amount,  # included
                            "currency": "UAH"
                        }
                    }
                ],
                "tenderers": [{
                    "identifier": {
                        "scheme": "spam",
                        "id": "ham",
                    }
                }]
            }
        ],
        "lots": [
            {"id": "lot1"},
            {"id": "lot2"},
            {"id": "lot3"},
            {"id": "lot999"},
        ]
    }}
    complaint["__parent__"] = cancellation

    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH",
                               "amount": round_up_to_ten(3 * amount * COMPLAINT_ENHANCED_AMOUNT_RATE)}


def test_esco_lot_related_but_passed_acc_token_from_different_bid():
    """
    Tenderer provides his token from a bid with low amount to confuse the system
    we should find his another bid and related lotValue anyway
    :return:
    """
    complaint = Complaint(complaint_data)
    amount = 901000

    class MyMock(Mock):
        def get(self, key):
            return getattr(self, key)
    root = Mock(__parent__=None)
    cancellation = MyMock(__parent__=root, relatedLot="lot999", lotID=None)
    root.request.params = {"acc_token": "secret_stuff"}
    root.request.logging_context.items.return_value = ""
    root.request.validated = {"tender": {
        "revisions": [Mock(date=RELEASE_2020_04_19 + timedelta(days=1))],
        "status": "active.qualification",
        "procurementMethodType": "esco",
        "bids": [
            {
                "owner_token": "secret_stuff",
                "lotValues": [
                    {
                        "relatedLot": "lot1",
                        "value": {
                            "amount": 100,
                            "currency": "UAH"
                        }
                    }
                ],
                "tenderers": [{
                    "identifier": {
                        "scheme": "spam",
                        "id": "ham",
                    }
                }]
            },
            {
                "owner_token": "another_secret_stuff",
                "lotValues": [
                    {
                        "relatedLot": "lot999",
                        "value": {
                            "amount": amount,
                            "currency": "UAH"
                        }
                    }
                ],
                "tenderers": [{
                    "identifier": {
                        "scheme": "spam",
                        "id": "ham",
                    }
                }]
            },
        ],
        "lots": [
            {"id": "lot1"},
            {"id": "lot999"},
        ]
    }}
    complaint["__parent__"] = cancellation

    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": round_up_to_ten(amount * COMPLAINT_ENHANCED_AMOUNT_RATE)}
