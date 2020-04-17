# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from uuid import uuid4

from datetime import timedelta

from openprocurement.api.constants import SANDBOX_MODE, RELEASE_2020_04_19
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.base import BaseCoreWebTest
from openprocurement.tender.belowthreshold.constants import MIN_BIDS_NUMBER
from openprocurement.tender.pricequotation.constants import PMT


now = get_now()
test_requirement_response_valid = [
    {
        "value": 23.8,
        'requirement': {
            'id': "655360-0001-001-01"
        }
    },
    {
        "value": "1920x1080",
        'requirement': {
            'id': "655360-0002-001-01"
        }
    },
    {
        "value": "16:9",
        'requirement': {
            'id': "655360-0003-001-01"
        }
    },
    {
        "value": 250,
        'requirement': {
            'id': "655360-0004-001-01"
        }
    },
    {
        "value": "1000:1",
        'requirement': {
            'id': "655360-0005-001-01"
        }
    },
    {
        "value": 1,
        'requirement': {
            'id': "655360-0006-001-01"
        }
    },
    {
        "value": 1,
        'requirement': {
            'id': "655360-0007-001-01"
        }
    },
    {
        "value": "HDMI",
        'requirement': {
            'id': "655360-0008-001-01"
        }
    },
    {
        "value": 36,
        'requirement': {
            'id': "655360-0009-001-01"
        }
    },
    {
        "value": "3000:1",
        'requirement': {
            "id": "655360-0005-002-01",
        }
    }
]

test_organization = {
    "name": u"Державне управління справами",
    "identifier": {"scheme": u"UA-EDR", "id": u"00037256", "uri": u"http://www.dus.gov.ua/"},
    "address": {
        "countryName": u"Україна",
        "postalCode": u"01220",
        "region": u"м. Київ",
        "locality": u"м. Київ",
        "streetAddress": u"вул. Банкова, 11, корпус 1",
    },
    "contactPoint": {"name": u"Державне управління справами", "telephone": u"0440000000"},
    "scale": "micro",
}

test_author = test_organization.copy()
del test_author["scale"]

test_procuringEntity = test_author.copy()
test_procuringEntity["kind"] = "general"
test_milestones = [
    {
        "id": "a" * 32,
        "title": "signingTheContract",
        "code": "prepayment",
        "type": "financing",
        "duration": {"days": 2, "type": "banking"},
        "sequenceNumber": 0,
        "percentage": 45.55,
    },
    {
        "title": "deliveryOfGoods",
        "code": "postpayment",
        "type": "financing",
        "duration": {"days": 900, "type": "calendar"},
        "sequenceNumber": 0,
        "percentage": 54.45,
    },
]

test_item = {
    "description": u"Комп’ютерне обладнання",
    "classification": {"scheme": u"ДК021", "id": u"44617100-9", "description": u"Cartons"},
    "additionalClassifications": [
        {"scheme": u"INN", "id": u"17.21.1", "description": u"папір і картон гофровані, паперова й картонна тара"}
    ],
    "quantity": 5,
    "deliveryDate": {
        "startDate": (now + timedelta(days=2)).isoformat(),
        "endDate": (now + timedelta(days=5)).isoformat(),
    },
    "deliveryAddress": {
        "countryName": u"Україна",
        "postalCode": "79000",
        "region": u"м. Київ",
        "locality": u"м. Київ",
        "streetAddress": u"вул. Банкова 1",
    },
}

test_tender_data = {
    "title": u"Комп’ютерне обладнання",
    "profile": "655360-30230000-889652-40000777",
    "mainProcurementCategory": "goods",
    "procuringEntity": test_procuringEntity,
    "value": {"amount": 500, "currency": u"UAH"},
    "items": [deepcopy(test_item)],
    "tenderPeriod": {"endDate": (now + timedelta(days=14)).isoformat()},
    "procurementMethodType": PMT,
    "milestones": test_milestones,
}
if SANDBOX_MODE:
    test_tender_data["procurementMethodDetails"] = "quick, accelerator=1440"
test_bids = [
    {"tenderers": [test_organization], "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True}, "requirementResponses": test_requirement_response_valid},
    {"tenderers": [test_organization], "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True}, "requirementResponses": test_requirement_response_valid},
]

test_cancellation = {
    "reason": "cancellation reason",
}
if RELEASE_2020_04_19 < get_now():
    test_cancellation.update({
        "reasonType": "noDemand"
    })

test_shortlisted_firms = [
    {
        "address": {
            "countryName": "Україна",
            "locality": "м.Київ",
            "postalCode": "01100",
            "region": "Київська область",
            "streetAddress": "бул.Дружби Народів, 8"
        },
        "contactPoint": {
            "email": "contact@pixel.pix",
            "name": "Оксана Піксель",
            "telephone": "(067) 123-45-67"
        },
        "id": "UA-EDR-12345678",
        "identifier": {
            "id": "12345678",
            "legalName": "Товариство з обмеженою відповідальністю «Пікселі»",
            "scheme": "UA-EDR"
        },
        "name": "Товариство з обмеженою відповідальністю «Пікселі»",
        "scale": "large",
        "status": "active"
    },
    {
        "address": {
            "countryName": "Україна",
            "locality": "м.Тернопіль",
            "postalCode": "46000",
            "region": "Тернопільська область",
            "streetAddress": "вул. Кластерна, 777-К"
        },
        "contactPoint": {
            "email": "info@shteker.pek",
            "name": "Олег Штекер",
            "telephone": "(095) 123-45-67"
        },
        "id": "UA-EDR-87654321",
        "identifier": {
            "id": "87654321",
            "legalName": "Товариство з обмеженою відповідальністю «Штекер-Пекер»",
            "scheme": "UA-EDR"
        },
        "name": "Товариство з обмеженою відповідальністю «Штекер-Пекер»",
        "scale": "large",
        "status": "active"
    }
]

test_short_profile = {
    "classification": {
        "description": "Комп’ютерне обладнанн",
        "id": "30230000-0",
        "scheme": "ДК021"
    },
    "id": "655360-30230000-889652-40000777",
    "unit": {
        "code": "H87",
        "name": "штук"
    },
    "criteria": [
        {
            "code": "OCDS-MONITOR-DIAGONAL",
            "description": "Діагональ екрану",
            "id": "655360-0001",
            "requirementGroups": [
                {
                    "description": "Діагональ екрану, не менше 23.8 дюймів",
                    "id": "655360-0001-001",
                    "requirements": [
                        {
                            "dataType": "number",
                            "id": "655360-0001-001-01",
                            "minValue": 23.8,
                            "title": "Діагональ екрану",
                            "unit": {
                                "code": "INH",
                                "name": "дюйм"
                            }
                        }
                    ]
                }
            ],
            "title": "Діагональ екрану"
        },
        {
            "code": "OCDS-MONITOR-RESOLUTION",
            "description": "Роздільна здатність",
            "id": "655360-0002",
            "requirementGroups": [
                {
                    "description": "Роздільна здатність - 1920x1080",
                    "id": "655360-0002-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "1920x1080",
                            "id": "655360-0002-001-01",
                            "title": "Роздільна здатність"
                        }
                    ]
                }
            ],
            "title": "Роздільна здатність"
        },
        {
            "code": "OCDS-MONITOR-CORRELATION",
            "description": "Співвідношення сторін",
            "id": "655360-0003",
            "requirementGroups": [
                {
                    "description": "Співвідношення сторін",
                    "id": "655360-0003-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "16:9",
                            "id": "655360-0003-001-01",
                            "title": "Співвідношення сторін"
                        }
                    ]
                }
            ],
            "title": "Співвідношення сторін"
        },
        {
            "code": "OCDS-MONITOR-BRIGHTNESS",
            "description": "Яскравість дисплея",
            "id": "655360-0004",
            "requirementGroups": [
                {
                    "description": "Яскравість дисплея, не менше 250 кд/м²",
                    "id": "655360-0004-001",
                    "requirements": [
                        {
                            "dataType": "integer",
                            "id": "655360-0004-001-01",
                            "minValue": 250,
                            "title": "Яскравість дисплея",
                            "unit": {
                                "code": "A24",
                                "name": "кд/м²"
                            }
                        }
                    ]
                }
            ],
            "title": "Яскравість дисплея"
        },
        {
            "code": "OCDS-MONITOR-CONTRAST",
            "description": "Контрастність (статична)",
            "id": "655360-0005",
            "requirementGroups": [
                {
                    "description": "Контрастність (статична) - 1000:1",
                    "id": "655360-0005-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "1000:1",
                            "id": "655360-0005-001-01",
                            "title": "Контрастність (статична)"
                        }
                    ]
                },
                {
                    "description": "Контрастність (статична) - 3000:1",
                    "id": "655360-0005-002",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "3000:1",
                            "id": "655360-0005-002-01",
                            "title": "Контрастність (статична)"
                        }
                    ]
                }
            ],
            "title": "Контрастність (статична)"
        },
        {
            "code": "OCDS-MONITOR-HDMI",
            "description": "Кількість портів HDMI",
            "id": "655360-0006",
            "requirementGroups": [
                {
                    "description": "Кількість портів HDMI, не менше 1 шт.",
                    "id": "655360-0006-001",
                    "requirements": [
                        {
                            "dataType": "integer",
                            "id": "655360-0006-001-01",
                            "minValue": 1,
                            "title": "Кількість портів HDMI",
                            "unit": {
                                "code": "H87",
                                "name": "штук"
                            }
                        }
                    ]
                }
            ],
            "title": "Кількість портів HDMI"
        },
        {
            "code": "OCDS-MONITOR-D-SUB",
            "description": "Кількість портів D-sub",
            "id": "655360-0007",
            "requirementGroups": [
                {
                    "description": "Кількість портів D-sub, не менше 1 шт.",
                    "id": "655360-0007-001",
                    "requirements": [
                        {
                            "dataType": "integer",
                            "id": "655360-0007-001-01",
                            "minValue": 1,
                            "title": "Кількість портів D-sub",
                            "unit": {
                                "code": "H87",
                                "name": "штук"
                            }
                        }
                    ]
                }
            ],
            "title": "Кількість портів D-sub"
        },
        {
            "code": "OCDS-MONITOR-HDMIPORT",
            "description": "Кабель для під’єднання",
            "id": "655360-0008",
            "requirementGroups": [
                {
                    "description": "Кабель для під’єднання",
                    "id": "655360-0008-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "HDMI",
                            "id": "655360-0008-001-01",
                            "title": "Кабель для під’єднання"
                        }
                    ]
                }
            ],
            "title": "Кабель для під’єднання"
        },
        {
            "code": "OCDS-MONITOR-GUARANTEE",
            "description": "Строк дії гарантії",
            "id": "655360-0009",
            "requirementGroups": [
                {
                    "description": "Гарантія, не менше 36 місяців",
                    "id": "655360-0009-001",
                    "requirements": [
                        {
                            "dataType": "integer",
                            "id": "655360-0009-001-01",
                            "minValue": 36,
                            "title": "Гарантія",
                            "unit": {
                                "code": "MON",
                                "name": "місяців"
                            }
                        }
                    ]
                }
            ],
            "title": "Гарантія"
        }
    ],
    "value": {
        "amount": 4500,
        "currency": "UAH",
        "valueAddedTaxIncluded": True
    }
}


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_auth = ("Basic", ("broker", ""))
    docservice = False
    min_bids_number = MIN_BIDS_NUMBER
    # Statuses for test, that will be imported from others procedures
    primary_tender_status = "draft.publishing"  # status, to which tender should be switched from 'draft'
    forbidden_document_modification_actions_status = (
        "active.qualification"
    )  # status, in which operations with tender documents (adding, updating) are forbidden
    forbidden_question_modification_actions_status = (
        "active.tendering"
    )  # status, in which adding/updating tender questions is forbidden
    forbidden_contract_document_modification_actions_status = (
        "unsuccessful"
    )  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    # auction role actions
    forbidden_auction_actions_status = (
        "active.tendering"
    )  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = (
        "active.tendering"
    )  # status, in which adding document to tender auction is forbidden

    def update_status(self, status, extra=None):
        now = get_now()
        data = {"status": status}
        if status == "active.tendering":
            items = deepcopy(self.initial_data["items"])
            for item in items:
                item.update({"classification": test_short_profile["classification"],
                             "unit": test_short_profile["unit"]})
            data.update(
                {
                    "tenderPeriod": {"startDate": (now).isoformat(), "endDate": (now + timedelta(days=1)).isoformat()},
                    "shortlistedFirms": test_shortlisted_firms,
                    'criteria': test_short_profile['criteria'],
                    "items": items
                }
            )
        elif status == "active.qualification":
            self.set_status("active.tendering")
            data.update(
                {
                    "tenderPeriod": {
                        "startDate": (now - timedelta(days=8)).isoformat(),
                        "endDate": (now - timedelta(days=1)).isoformat(),
                    },
                    "awardPeriod": {"startDate": (now).isoformat()},
                }
            )
        elif status == "active.awarded":
            self.set_status("active.qualification")
            data.update(
                {
                    "tenderPeriod": {
                        "startDate": (now - timedelta(days=8)).isoformat(),
                        "endDate": (now - timedelta(days=1)).isoformat(),
                    },
                    "awardPeriod": {"startDate": (now).isoformat(), "endDate": (now).isoformat()},
                }
            )
        elif status == "complete":
            self.set_status("active.awarded")
            data.update(
                {
                    "tenderPeriod": {
                        "startDate": (now - timedelta(days=18)).isoformat(),
                        "endDate": (now - timedelta(days=11)).isoformat(),
                    },
                    "awardPeriod": {
                        "startDate": (now - timedelta(days=10)).isoformat(),
                        "endDate": (now - timedelta(days=10)).isoformat(),
                    },
                }
            )

        self.tender_document_patch = data
        if extra:
            self.tender_document_patch.update(extra)
        self.save_changes()

    def create_tender(self):
        data = deepcopy(self.initial_data)
        response = self.app.post_json("/tenders", {"data": data})
        tender = response.json["data"]
        self.tender_token = response.json["access"]["token"]
        self.tender_id = tender["id"]
        status = tender["status"]
        if self.initial_status and self.initial_status != status:
            self.set_status(self.initial_status)

        if self.initial_bids:
            self.initial_bids_tokens = {}
            response = self.set_status("active.tendering")
            status = response.json["data"]["status"]
            bids = []
            for bid in self.initial_bids:
                response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid})
                self.assertEqual(response.status, "201 Created")
                bids.append(response.json["data"])
                self.initial_bids_tokens[response.json["data"]["id"]] = response.json["access"]["token"]
            self.initial_bids = bids


class TenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None

    def setUp(self):
        super(TenderContentWebTest, self).setUp()
        self.create_tender()
