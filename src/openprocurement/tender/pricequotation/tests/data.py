# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime, timedelta
from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.constants import PMT
from openprocurement.api.constants import SANDBOX_MODE, RELEASE_2020_04_19


now = get_now()


PERIODS = {
    "active.tendering": {
        "start": {
            "tenderPeriod": {
                "startDate": -timedelta(),
                "endDate": timedelta(days=1)
            },
        },
        "end": {
            "tenderPeriod": {
                "startDate": - timedelta(days=1),
                "endDate": timedelta()
            },
        },
    },
    "active.qualification": {
        "start": {
            "tenderPeriod": {
                "startDate": - timedelta(days=2),
                "endDate": - timedelta(days=1),
            },
            "awardPeriod": {"startDate": timedelta()},
        },
        "end": {
            "tenderPeriod": {
                "startDate": - timedelta(days=2),
                "endDate": - timedelta(days=1),
            },
            "awardPeriod": {"startDate": timedelta()},
        },
    },
    "active.awarded": {
        "start": {
            "tenderPeriod": {
                "startDate": - timedelta(days=2),
                "endDate": - timedelta(days=1),
            },
            "awardPeriod": {"startDate": timedelta(), "endDate": timedelta()},
        },
        "end": {
            "tenderPeriod": {
                "startDate": - timedelta(days=3),
                "endDate": - timedelta(days=2),
            },
            "awardPeriod": {
                "startDate": - timedelta(days=1),
                "endDate": - timedelta(days=1),
            },
        },
    },
    "complete": {
        "start": {
            "tenderPeriod": {
                "startDate": - timedelta(days=2),
                "endDate": - timedelta(days=1)
            },
            "awardPeriod": {
                "startDate": - timedelta(days=1),
                "endDate": -timedelta(),
            },
        }
    },
}


test_requirement_response_valid = [
    {
        "value": "23.8",
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

test_author = test_organization.copy()
del test_author["scale"]

test_procuringEntity = test_author.copy()
test_procuringEntity["kind"] = "general"

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
                            "minValue": "23.8",
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
