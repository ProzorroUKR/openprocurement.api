# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from copy import deepcopy
from datetime import timedelta
from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.constants import PMT
from openprocurement.api.constants import SANDBOX_MODE


now = get_now()


PERIODS = {
    "active.tendering": {
        "start": {
            "tenderPeriod": {
                "startDate": -timedelta(),
                "endDate": timedelta(days=6)
            },
        },
        "end": {
            "tenderPeriod": {
                "startDate": - timedelta(days=6),
                "endDate": timedelta()
            },
        },
    },
    "active.qualification": {
        "start": {
            "tenderPeriod": {
                "startDate": - timedelta(days=10),
                "endDate": - timedelta(days=1),
            },
            "awardPeriod": {"startDate": timedelta()},
        },
        "end": {
            "tenderPeriod": {
                "startDate": - timedelta(days=10),
                "endDate": - timedelta(days=1),
            },
            "awardPeriod": {"startDate": timedelta()},
        },
    },
    "active.awarded": {
        "start": {
            "tenderPeriod": {
                "startDate": - timedelta(days=10),
                "endDate": - timedelta(days=1),
            },
            "awardPeriod": {"startDate": timedelta(), "endDate": timedelta()},
        },
        "end": {
            "tenderPeriod": {
                "startDate": - timedelta(days=10),
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
                "startDate": - timedelta(days=10),
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
    "quantity": 1,
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
    "items": [deepcopy(test_item)],
    "value": {"amount": 22000, "currency": "UAH"},
    "tenderPeriod": {"endDate": (now + timedelta(days=14)).isoformat()},
    "procurementMethodType": PMT,
    "procurementMethod": 'selective',
}
if SANDBOX_MODE:
    test_tender_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_bids = [
    {"tenderers": [test_organization], "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True}, "requirementResponses": test_requirement_response_valid},
    {"tenderers": [test_organization], "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True}, "requirementResponses": test_requirement_response_valid},
]
bid_with_docs = deepcopy(test_bids[1])
bid_with_docs["documents"] = [
    {
        'title': u'Proposal_part1.pdf',
        'url': u"http://broken1.ds",
        'hash': 'md5:' + '0' * 32,
        'format': 'application/pdf',
    },
    {
        'title': u'Proposal_part2.pdf',
        'url': u"http://broken2.ds",
        'hash': 'md5:' + '0' * 32,
        'format': 'application/pdf',
    }
]

test_cancellation = {
    "reason": "cancellation reason",
    "reasonType": "noDemand",
    "cancellationOf": "tender",
}


test_shortlisted_firms = [
    {
        "address": {
            "countryName": u"Україна",
            "locality": u"м.Київ",
            "postalCode": "01100",
            "region": u"Київська область",
            "streetAddress": u"бул.Дружби Народів, 8"
        },
        "contactPoint": {
            "email": "contact@pixel.pix",
            "name": u"Оксана Піксель",
            "telephone": "(067) 123-45-67"
        },
        "id": "UA-EDR-12345678",
        "identifier": {
            "id": "12345678",
            "legalName": u"Товариство з обмеженою відповідальністю «Пікселі»",
            "scheme": "UA-EDR"
        },
        "name": u"Товариство з обмеженою відповідальністю «Пікселі»",
        "scale": "large",
        "status": "active"
    },
    {
        "address": {
            "countryName": u"Україна",
            "locality": u"м.Тернопіль",
            "postalCode": "46000",
            "region": u"Тернопільська область",
            "streetAddress": u"вул. Кластерна, 777-К"
        },
        "contactPoint": {
            "email": "info@shteker.pek",
            "name": u"Олег Штекер",
            "telephone": "(095) 123-45-67"
        },
        "id": "UA-EDR-87654321",
        "identifier": {
            "id": "87654321",
            "legalName": u"Товариство з обмеженою відповідальністю «Штекер-Пекер»",
            "scheme": "UA-EDR"
        },
        "name": u"Товариство з обмеженою відповідальністю «Штекер-Пекер»",
        "scale": "large",
        "status": "active"
    }
]

test_short_profile = {
    "classification": {
        "description": u"Комп’ютерне обладнанн",
        "id": "30230000-0",
        "scheme": u"ДК021"
    },
    "id": "655360-30230000-889652-40000777",
    "unit": {
        "code": "H87",
        "name": u"штук"
    },
    "criteria": [
        {
            "description": u"Діагональ екрану",
            "id": "655360-0001",
            "requirementGroups": [
                {
                    "description": u"Діагональ екрану, не менше 23.8 дюймів",
                    "id": "655360-0001-001",
                    "requirements": [
                        {
                            "dataType": "number",
                            "id": "655360-0001-001-01",
                            "minValue": "23.8",
                            "title": u"Діагональ екрану",
                            "unit": {
                                "code": "INH",
                                "name": u"дюйм"
                            }
                        }
                    ]
                }
            ],
            "title": u"Діагональ екрану"
        },
        {
            "description": u"Роздільна здатність",
            "id": "655360-0002",
            "requirementGroups": [
                {
                    "description": u"Роздільна здатність - 1920x1080",
                    "id": "655360-0002-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "1920x1080",
                            "id": "655360-0002-001-01",
                            "title": u"Роздільна здатність"
                        }
                    ]
                }
            ],
            "title": u"Роздільна здатність"
        },
        {
            "description": u"Співвідношення сторін",
            "id": "655360-0003",
            "requirementGroups": [
                {
                    "description": u"Співвідношення сторін",
                    "id": "655360-0003-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "16:9",
                            "id": "655360-0003-001-01",
                            "title": u"Співвідношення сторін"
                        }
                    ]
                }
            ],
            "title": u"Співвідношення сторін"
        },
        {
            "description": u"Яскравість дисплея",
            "id": "655360-0004",
            "requirementGroups": [
                {
                    "description": u"Яскравість дисплея, не менше 250 кд/м²",
                    "id": "655360-0004-001",
                    "requirements": [
                        {
                            "dataType": "integer",
                            "id": "655360-0004-001-01",
                            "maxValue": 250,
                            "title": "Яскравість дисплея",
                            "unit": {
                                "code": "A24",
                                "name": u"кд/м²"
                            }
                        }
                    ]
                }
            ],
            "title": u"Яскравість дисплея"
        },
        {
            "description": u"Контрастність (статична)",
            "id": "655360-0005",
            "requirementGroups": [
                {
                    "description": u"Контрастність (статична) - 1000:1",
                    "id": "655360-0005-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "1000:1",
                            "id": "655360-0005-001-01",
                            "title": u"Контрастність (статична)"
                        }
                    ]
                },
                {
                    "description": u"Контрастність (статична) - 3000:1",
                    "id": "655360-0005-002",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "3000:1",
                            "id": "655360-0005-002-01",
                            "title": u"Контрастність (статична)"
                        }
                    ]
                }
            ],
            "title": u"Контрастність (статична)"
        },
        {
            "description": u"Кількість портів HDMI",
            "id": "655360-0006",
            "requirementGroups": [
                {
                    "description": u"Кількість портів HDMI, не менше 1 шт.",
                    "id": "655360-0006-001",
                    "requirements": [
                        {
                            "dataType": "integer",
                            "id": "655360-0006-001-01",
                            "minValue": 1,
                            "title": u"Кількість портів HDMI",
                            "unit": {
                                "code": "H87",
                                "name": u"штук"
                            }
                        }
                    ]
                }
            ],
            "title": u"Кількість портів HDMI"
        },
        {
            "description": u"Кількість портів D-sub",
            "id": "655360-0007",
            "requirementGroups": [
                {
                    "description": u"Кількість портів D-sub, не менше 1 шт.",
                    "id": "655360-0007-001",
                    "requirements": [
                        {
                            "dataType": "integer",
                            "id": "655360-0007-001-01",
                            "minValue": 1,
                            "title": u"Кількість портів D-sub",
                            "unit": {
                                "code": "H87",
                                "name": u"штук"
                            }
                        }
                    ]
                }
            ],
            "title": u"Кількість портів D-sub"
        },
        {
            "description": u"Кабель для під’єднання",
            "id": "655360-0008",
            "requirementGroups": [
                {
                    "description": u"Кабель для під’єднання",
                    "id": "655360-0008-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "HDMI",
                            "id": "655360-0008-001-01",
                            "title": u"Кабель для під’єднання"
                        }
                    ]
                }
            ],
            "title": u"Кабель для під’єднання"
        },
        {
            "description": u"Строк дії гарантії",
            "id": "655360-0009",
            "requirementGroups": [
                {
                    "description": u"Гарантія, не менше 36 місяців",
                    "id": "655360-0009-001",
                    "requirements": [
                        {
                            "dataType": "integer",
                            "id": "655360-0009-001-01",
                            "minValue": 36,
                            "title": u"Гарантія",
                            "unit": {
                                "code": "MON",
                                "name": u"місяців"
                            }
                        }
                    ]
                }
            ],
            "title": u"Гарантія"
        }
    ],
    "value": {
        "amount": 500,
        "currency": "UAH",
        "valueAddedTaxIncluded": True
    }
}


test_criteria_1 = [
    {
        "description": u"Форма випуску",
        "id": "400496-0001",
        "requirementGroups": [
            {
                "description": u"Форма випуску",
                "id": "400496-0001-001",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": u"Розчин для інфузій",
                        "id": "400496-0001-001-01",
                        "title": u"Форма випуску"
                    }
                ]
            }
        ],
        "title": u"Форма випуску"
    },
    {
        "description": u"Доза діючої речовини",
        "id": "400496-0002",
        "requirementGroups": [
            {
                "description": u"Доза діючої речовини",
                "id": "400496-0002-001",
                "requirements": [
                    {
                        "dataType": "integer",
                        "minValue": 5,
                        "id": "400496-0002-001-01",
                        "title": u"Доза діючої речовини",
                        "unit": {
                            "code": "GL",
                            "name": "г/л"
                        }
                    }
                ]
            }
        ],
        "title": u"Доза діючої речовини"
    }
]

test_criteria_2 = [
    {
        "description": u"Форма випуску",
        "id": "400496-0001",
        "requirementGroups": [
            {
                "description": u"Форма випуску",
                "id": "400496-0001-001",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": u"Розчин",
                        "id": "400496-0001-001-01",
                        "title": u"Форма випуску"
                    }
                ]
            },
            {
                "description": u"Форма випуску",
                "id": "400496-0001-002",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": u"Порошок",
                        "id": "400496-0001-002-01",
                        "title": u"Форма випуску"
                    }
                ]
            }
        ],
        "title": u"Форма випуску"
    }
]


test_criteria_3 = [
    {
        "description": u"Форма випуску",
        "id": "400496-0001",
        "requirementGroups": [
            {
                "description": u"Форма випуску",
                "id": "400496-0001-001",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": u"Розчин",
                        "id": "400496-0001-001-01",
                        "title": u"Форма випуску"
                    },
                    {
                        "dataType": "integer",
                        "expectedValue": 500,
                        "id": "400496-0001-001-02",
                        "title": u"Форма випуску",
                        "unit": {
                            "code": "MLT",
                            "name": u"мл"
                        }
                    }
                ]
            },
            {
                "description": u"Форма випуску",
                "id": "400496-0001-002",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": u"Порошок",
                        "id": "400496-0001-002-01",
                        "title": u"Форма випуску"
                    }
                ]
            }
        ],
        "title": u"Форма випуску"
    }]


test_criteria_4 = [
    {
        "description": u"Форма випуску",
        "title": u"Форма випуску",
        "id": "400496-0001",
        "requirementGroups": [
            {
                "description": u"Форма випуску",
                "id": "400496-0001-001",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": u"Розчин",
                        "id": "400496-0001-001-01",
                        "title": u"Форма випуску"
                    },
                    {
                        "dataType": "integer",
                        "expectedValue": 500,
                        "id": "400496-0001-001-02",
                        "title": u"Форма випуску",
                        "unit": {
                            "code": "MLT",
                            "name": u"мл"
                        },
                    },
                    {
                        "dataType": "integer",
                        "expectedValue": 1,
                        "id": "400496-0001-001-03",
                        "title": u"Форма випуску",
                        "unit": {
                            "code": "H87",
                            "name": u"ШТ"
                        }
                    }
                ]
            }
        ]
    }
]


test_response_1 = [
    {
        "requirement": {
            "id": "400496-0001-001-01"
        },
        "value": u"Розчин для інфузій"
    },
    {
        "requirement": {
            "id": "400496-0002-001-01"
        },
        "value": 5
    }
]


test_response_2_1 = [
    {
        "requirement": {
            "id": "400496-0001-001-01"
        },
        "value": u"Розчин"
    }
]


test_response_2_2 = [
    {
        "requirement": {
            "id": "400496-0001-002-01"
        },
        "value": u"Порошок"
    }
]


test_response_3_1 = [
    {
        "requirement": {
            "id": "400496-0001-001-01"
        },
        "value": u"Розчин"
    },
    {
        "requirement": {
            "id": "400496-0001-001-02"
        },
        "value": 500
    }
]


test_response_3_2 = [
    {
        "requirement": {
            "id": "400496-0001-002-01"
        },
        "value": u"Порошок"
    }
]


test_response_4 = [
    {
        "requirement": {
            "id": "400496-0001-001-01"
        },
        "value": u"Порошок"
    },
    {
        "requirement": {
            "id": "400496-0001-001-02"
        },
        "value": 500
    },
    {
        "requirement": {
            "id": "400496-0001-001-03"
        },
        "value": 1
    }
]
