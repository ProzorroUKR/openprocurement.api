from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.utils import set_tender_multi_buyers
from openprocurement.tender.pricequotation.constants import PQ

now = get_now()

test_agreement_pq_data = {
    "_id": "2e14a78a2074952d5a2d256c3c004dda",
    "doc_type": "Agreement",
    "agreementID": "UA-2021-11-12-000001",
    "agreementType": "electronicCatalogue",
    "frameworkID": "985a2e3eab47427283a5c51e84d0986d",
    "period": {"startDate": "2021-11-12T00:00:00.318051+02:00", "endDate": "2022-02-24T20:14:24.577158+03:00"},
    "status": "active",
    "contracts": [
        {
            "id": "eb228ceafee5470ca947af3fc2c03662",
            "status": "active",
            "suppliers": [
                {
                    "address": {
                        "countryName": "Україна",
                        "locality": "м.Київ",
                        "postalCode": "01100",
                        "region": "Київська область",
                        "streetAddress": "бул.Дружби Народів, 8",
                    },
                    "contactPoint": {
                        "email": "contact@pixel.pix",
                        "name": "Оксана Піксель",
                        "telephone": "+0671234567",
                    },
                    "id": "UA-EDR-12345678",
                    "identifier": {
                        "id": "00037256",
                        "legalName": "Товариство з обмеженою відповідальністю «Пікселі»",
                        "scheme": "UA-IPN",
                    },
                    "name": "Товариство з обмеженою відповідальністю «Пікселі»",
                    "scale": "large",
                }
            ],
        },
        {
            "id": "4dcabeaff7714881a9e2275e3b4eefcc",
            "status": "active",
            "suppliers": [
                {
                    "address": {
                        "countryName": "Україна",
                        "locality": "м.Тернопіль",
                        "postalCode": "46000",
                        "region": "Тернопільська область",
                        "streetAddress": "вул. Кластерна, 777-К",
                    },
                    "contactPoint": {"email": "info@shteker.pek", "name": "Олег Штекер", "telephone": "+0951234567"},
                    "id": "UA-EDR-87654321",
                    "identifier": {
                        "id": "87654321",
                        "legalName": "Товариство з обмеженою відповідальністю «Штекер-Пекер»",
                        "scheme": "UA-IPN",
                    },
                    "name": "Товариство з обмеженою відповідальністю «Штекер-Пекер»",
                    "scale": "large",
                }
            ],
        },
    ],
}

PERIODS = {
    "active.tendering": {
        "start": {
            "tenderPeriod": {"startDate": -timedelta(), "endDate": timedelta(days=8)},
        },
        "end": {
            "tenderPeriod": {"startDate": -timedelta(days=8), "endDate": timedelta()},
        },
    },
    "active.qualification": {
        "start": {
            "tenderPeriod": {
                "startDate": -timedelta(days=10),
                "endDate": -timedelta(days=1),
            },
            "awardPeriod": {"startDate": timedelta()},
        },
        "end": {
            "tenderPeriod": {
                "startDate": -timedelta(days=10),
                "endDate": -timedelta(days=1),
            },
            "awardPeriod": {"startDate": timedelta()},
        },
    },
    "active.awarded": {
        "start": {
            "tenderPeriod": {
                "startDate": -timedelta(days=10),
                "endDate": -timedelta(days=1),
            },
            "awardPeriod": {"startDate": timedelta(), "endDate": timedelta()},
        },
        "end": {
            "tenderPeriod": {
                "startDate": -timedelta(days=10),
                "endDate": -timedelta(days=2),
            },
            "awardPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": -timedelta(days=1),
            },
        },
    },
    "complete": {
        "start": {
            "tenderPeriod": {"startDate": -timedelta(days=10), "endDate": -timedelta(days=1)},
            "awardPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": -timedelta(),
            },
        }
    },
}


test_tender_pq_requirement_response_valid = [
    {"value": 23.8, 'requirement': {'id': "655360-0001-001-01"}},
    {"value": "1920x1080", 'requirement': {'id': "655360-0002-001-01"}},
    {"value": "16:9", 'requirement': {'id': "655360-0003-001-01"}},
    {"value": 250, 'requirement': {'id': "655360-0004-001-01"}},
    {"value": "1000:1", 'requirement': {'id': "655360-0005-001-01"}},
    {"value": 1, 'requirement': {'id': "655360-0006-001-01"}},
    {"value": 1, 'requirement': {'id': "655360-0007-001-01"}},
    {"value": "HDMI", 'requirement': {'id': "655360-0008-001-01"}},
    {"value": 36, 'requirement': {'id': "655360-0009-001-01"}},
]

test_tender_pq_criteria = [
    {
        "description": "Діагональ екрану",
        "source": "tenderer",
        "classification": {"scheme": " espd211", "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES1"},
        "legislation": [
            {
                "version": "2020-04-19",
                "identifier": {
                    "id": "922-VIII",
                    "legalName": "Закон України \"Про публічні закупівлі\"",
                    "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                },
                "type": "NATIONAL_LEGISLATION",
            }
        ],
        "requirementGroups": [
            {
                "description": "Діагональ екрану, не менше 23.8 дюймів",
                "requirements": [
                    {
                        "dataType": "number",
                        "id": "a" * 32,
                        "minValue": 23.8,
                        "title": "Діагональ екрану",
                        "unit": {"code": "INH", "name": "дюйм"},
                    }
                ],
            }
        ],
        "title": "Діагональ екрану",
    },
    {
        "description": "Роздільна здатність",
        "source": "tenderer",
        "classification": {"scheme": " espd211", "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES2"},
        "legislation": [
            {
                "version": "2020-04-19",
                "identifier": {
                    "id": "922-VIII",
                    "legalName": "Закон України \"Про публічні закупівлі\"",
                    "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                },
                "type": "NATIONAL_LEGISLATION",
            }
        ],
        "requirementGroups": [
            {
                "description": "Роздільна здатність - 1920x1080",
                "requirements": [
                    {"dataType": "string", "expectedValue": "1920x1080", "id": "b" * 32, "title": "Роздільна здатність"}
                ],
            }
        ],
        "title": "Роздільна здатність",
    },
]
test_tender_pq_requirement_response = [
    {"value": 23.8, 'requirement': {'id': "a" * 32}},
    {"value": "1920x1080", 'requirement': {'id': "b" * 32}},
]

test_tender_pq_organization = {
    "name": "Державне управління справами",
    "identifier": {"scheme": "UA-IPN", "id": "00037256", "uri": "http://www.dus.gov.ua/"},
    "address": {
        "countryName": "Україна",
        "postalCode": "01220",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова, 11, корпус 1",
    },
    "contactPoint": {"name": "Державне управління справами", "telephone": "+0440000000"},
    "scale": "micro",
}


test_tender_pq_milestones = [
    {
        "id": "a" * 32,
        "title": "signingTheContract",
        "code": "prepayment",
        "type": "financing",
        "duration": {"days": 2, "type": "banking"},
        "sequenceNumber": 1,
        "percentage": 45.55,
    },
    {
        "title": "deliveryOfGoods",
        "code": "postpayment",
        "type": "financing",
        "duration": {"days": 900, "type": "calendar"},
        "sequenceNumber": 2,
        "percentage": 54.45,
    },
]

test_tender_pq_author = test_tender_pq_organization.copy()
del test_tender_pq_author["scale"]

test_tender_pq_procuring_entity = test_tender_pq_author.copy()
test_tender_pq_procuring_entity["kind"] = "general"

test_tender_pq_item = {
    "description": "Комп’ютерне обладнання",
    "category": "655360-30230000-889652",
    "profile": "655360-30230000-889652-40000777",
    "quantity": 5,
    "deliveryDate": {
        "startDate": (now + timedelta(days=2)).isoformat(),
        "endDate": (now + timedelta(days=5)).isoformat(),
    },
    "unit": {
        "name": "кг",
        "code": "KGM",
        "value": {"amount": 6},
    },
    "deliveryAddress": {
        "countryName": "Україна",
        "postalCode": "79000",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова 1",
    },
    "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
    "additionalClassifications": [
        {
            "scheme": "INN",
            "id": "17.21.1",
            "description": "папір і картон гофровані, паперова й картонна тара",
        },
    ],
}

test_tender_pq_data = {
    "title": "Комп’ютерне обладнання",
    "mainProcurementCategory": "goods",
    "procuringEntity": test_tender_pq_procuring_entity,
    "value": {"amount": 22000, "currency": "UAH"},
    "tenderPeriod": {"endDate": (now + timedelta(days=14)).isoformat()},
    "procurementMethodType": PQ,
    "procurementMethod": 'selective',
    "items": [test_tender_pq_item],
    "agreement": {"id": "0" * 32},
}

if SANDBOX_MODE:
    test_tender_pq_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_pq_multi_buyers_data = set_tender_multi_buyers(
    test_tender_pq_data, test_tender_pq_data["items"][0], test_tender_pq_organization
)

test_tender_pq_bids = [
    {
        "tenderers": [test_tender_pq_organization],
        "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
        "requirementResponses": test_tender_pq_requirement_response,
    },
    {
        "tenderers": [test_tender_pq_organization],
        "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True},
        "requirementResponses": test_tender_pq_requirement_response,
    },
]

test_tender_pq_bids_with_docs = deepcopy(test_tender_pq_bids[1])
test_tender_pq_bids_with_docs["documents"] = [
    {
        'title': 'Proposal_part1.pdf',
        'url': "http://broken1.ds",
        'hash': 'md5:' + '0' * 32,
        'format': 'application/pdf',
    },
    {
        'title': 'Proposal_part2.pdf',
        'url': "http://broken2.ds",
        'hash': 'md5:' + '0' * 32,
        'format': 'application/pdf',
    },
]

test_tender_pq_config = {
    "hasAuction": False,
    "hasAwardingOrder": True,
    "hasValueRestriction": True,
    "valueCurrencyEquality": True,
    "hasPrequalification": False,
    "minBidsNumber": 1,
    "hasPreSelectionAgreement": True,
    "hasTenderComplaints": False,
    "hasAwardComplaints": False,
    "hasCancellationComplaints": False,
    "hasValueEstimation": True,
    "hasQualificationComplaints": False,
    "tenderComplainRegulation": 0,
    "qualificationComplainDuration": 0,
    "awardComplainDuration": 0,
    "cancellationComplainDuration": 0,
    "clarificationUntilDuration": 0,
    "qualificationDuration": 0,
    "restricted": False,
}

test_tender_pq_cancellation = {
    "reason": "cancellation reason",
    "reasonType": "noDemand",
    "cancellationOf": "tender",
}

test_tender_pq_shortlisted_firms = [
    {
        "address": {
            "countryName": "Україна",
            "locality": "м.Київ",
            "postalCode": "01100",
            "region": "Київська область",
            "streetAddress": "бул.Дружби Народів, 8",
        },
        "contactPoint": {"email": "contact@pixel.pix", "name": "Оксана Піксель", "telephone": "+0671234567"},
        "id": "UA-EDR-12345678",
        "identifier": {
            "id": "00037256",
            "legalName": "Товариство з обмеженою відповідальністю «Пікселі»",
            "scheme": "UA-IPN",
        },
        "name": "Товариство з обмеженою відповідальністю «Пікселі»",
        "scale": "large",
        "status": "active",
    },
    {
        "address": {
            "countryName": "Україна",
            "locality": "м.Тернопіль",
            "postalCode": "46000",
            "region": "Тернопільська область",
            "streetAddress": "вул. Кластерна, 777-К",
        },
        "contactPoint": {"email": "info@shteker.pek", "name": "Олег Штекер", "telephone": "+0951234567"},
        "id": "UA-EDR-87654321",
        "identifier": {
            "id": "87654321",
            "legalName": "Товариство з обмеженою відповідальністю «Штекер-Пекер»",
            "scheme": "UA-IPN",
        },
        "name": "Товариство з обмеженою відповідальністю «Штекер-Пекер»",
        "scale": "large",
        "status": "active",
    },
]

test_tender_pq_short_profile = {
    "classification": {"description": "Комп’ютерне обладнання", "id": "30230000-0", "scheme": "ДК021"},
    "id": "655360-30230000-889652-40000777",
    "relatedCategory": "655360-30230000-889652",
    "unit": {"code": "H87", "name": "штук"},
    "criteria": [
        {
            "description": "Діагональ екрану",
            "id": "655360-0001",
            "source": "tenderer",
            "classification": {
                "scheme": " espd211",
                "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES1",
            },
            "legislation": [
                {
                    "version": "2020-04-19",
                    "identifier": {
                        "id": "922-VIII",
                        "legalName": "Закон України \"Про публічні закупівлі\"",
                        "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                    },
                    "type": "NATIONAL_LEGISLATION",
                }
            ],
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
                            "unit": {"code": "INH", "name": "дюйм"},
                        }
                    ],
                }
            ],
            "title": "Діагональ екрану",
        },
        {
            "description": "Роздільна здатність",
            "id": "655360-0002",
            "classification": {
                "scheme": " espd211",
                "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES2",
            },
            "source": "tenderer",
            "legislation": [
                {
                    "version": "2020-04-19",
                    "identifier": {
                        "id": "922-VIII",
                        "legalName": "Закон України \"Про публічні закупівлі\"",
                        "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                    },
                    "type": "NATIONAL_LEGISLATION",
                }
            ],
            "requirementGroups": [
                {
                    "description": "Роздільна здатність - 1920x1080",
                    "id": "655360-0002-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "1920x1080",
                            "id": "655360-0002-001-01",
                            "title": "Роздільна здатність",
                        }
                    ],
                }
            ],
            "title": "Роздільна здатність",
        },
        {
            "description": "Співвідношення сторін",
            "id": "655360-0003",
            "classification": {
                "scheme": " espd211",
                "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES3",
            },
            "source": "tenderer",
            "legislation": [
                {
                    "version": "2020-04-19",
                    "identifier": {
                        "id": "922-VIII",
                        "legalName": "Закон України \"Про публічні закупівлі\"",
                        "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                    },
                    "type": "NATIONAL_LEGISLATION",
                }
            ],
            "requirementGroups": [
                {
                    "description": "Співвідношення сторін",
                    "id": "655360-0003-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "16:9",
                            "id": "655360-0003-001-01",
                            "title": "Співвідношення сторін",
                        }
                    ],
                }
            ],
            "title": "Співвідношення сторін",
        },
        {
            "description": "Яскравість дисплея",
            "id": "655360-0004",
            "classification": {
                "scheme": " espd211",
                "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES4",
            },
            "source": "tenderer",
            "legislation": [
                {
                    "version": "2020-04-19",
                    "identifier": {
                        "id": "922-VIII",
                        "legalName": "Закон України \"Про публічні закупівлі\"",
                        "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                    },
                    "type": "NATIONAL_LEGISLATION",
                }
            ],
            "requirementGroups": [
                {
                    "description": "Яскравість дисплея, не менше 250 кд/м²",
                    "id": "655360-0004-001",
                    "requirements": [
                        {
                            "dataType": "integer",
                            "id": "655360-0004-001-01",
                            "maxValue": 250,
                            "title": "Яскравість дисплея",
                            "unit": {"code": "A24", "name": "кд/м²"},
                        }
                    ],
                }
            ],
            "title": "Яскравість дисплея",
        },
        {
            "description": "Контрастність (статична)",
            "id": "655360-0005",
            "classification": {
                "scheme": " espd211",
                "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES5",
            },
            "source": "tenderer",
            "legislation": [
                {
                    "version": "2020-04-19",
                    "identifier": {
                        "id": "922-VIII",
                        "legalName": "Закон України \"Про публічні закупівлі\"",
                        "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                    },
                    "type": "NATIONAL_LEGISLATION",
                }
            ],
            "requirementGroups": [
                {
                    "description": "Контрастність (статична) - 1000:1",
                    "id": "655360-0005-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "1000:1",
                            "id": "655360-0005-001-01",
                            "title": "Контрастність (статична)",
                        }
                    ],
                }
            ],
            "title": "Контрастність (статична)",
        },
        {
            "description": "Кількість портів HDMI",
            "id": "655360-0006",
            "classification": {
                "scheme": " espd211",
                "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES6",
            },
            "source": "tenderer",
            "legislation": [
                {
                    "version": "2020-04-19",
                    "identifier": {
                        "id": "922-VIII",
                        "legalName": "Закон України \"Про публічні закупівлі\"",
                        "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                    },
                    "type": "NATIONAL_LEGISLATION",
                }
            ],
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
                            "unit": {"code": "H87", "name": "штук"},
                        }
                    ],
                }
            ],
            "title": "Кількість портів HDMI",
        },
        {
            "description": "Кількість портів D-sub",
            "id": "655360-0007",
            "classification": {
                "scheme": " espd211",
                "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES7",
            },
            "source": "tenderer",
            "legislation": [
                {
                    "version": "2020-04-19",
                    "identifier": {
                        "id": "922-VIII",
                        "legalName": "Закон України \"Про публічні закупівлі\"",
                        "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                    },
                    "type": "NATIONAL_LEGISLATION",
                }
            ],
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
                            "unit": {"code": "H87", "name": "штук"},
                        }
                    ],
                }
            ],
            "title": "Кількість портів D-sub",
        },
        {
            "description": "Кабель для під’єднання",
            "id": "655360-0008",
            "classification": {
                "scheme": " espd211",
                "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES8",
            },
            "source": "tenderer",
            "legislation": [
                {
                    "version": "2020-04-19",
                    "identifier": {
                        "id": "922-VIII",
                        "legalName": "Закон України \"Про публічні закупівлі\"",
                        "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                    },
                    "type": "NATIONAL_LEGISLATION",
                }
            ],
            "requirementGroups": [
                {
                    "description": "Кабель для під’єднання",
                    "id": "655360-0008-001",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValue": "HDMI",
                            "id": "655360-0008-001-01",
                            "title": "Кабель для під’єднання",
                        }
                    ],
                }
            ],
            "title": "Кабель для під’єднання",
        },
        {
            "description": "Строк дії гарантії",
            "id": "655360-0009",
            "classification": {
                "scheme": " espd211",
                "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES9",
            },
            "source": "tenderer",
            "legislation": [
                {
                    "version": "2020-04-19",
                    "identifier": {
                        "id": "922-VIII",
                        "legalName": "Закон України \"Про публічні закупівлі\"",
                        "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                    },
                    "type": "NATIONAL_LEGISLATION",
                }
            ],
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
                            "unit": {"code": "MON", "name": "місяців"},
                        }
                    ],
                }
            ],
            "title": "Гарантія",
        },
    ],
    "value": {"amount": 500, "currency": "UAH", "valueAddedTaxIncluded": True},
    "status": "active",
    "agreementID": "2e14a78a2074952d5a2d256c3c004dda",
}

test_tender_pq_category = {
    "classification": {"description": "Комп’ютерне обладнання", "id": "30230000-0", "scheme": "ДК021"},
    "id": "655360-30230000-889652",
    "status": "active",
    "criteria": deepcopy(test_tender_pq_short_profile["criteria"]),
}

test_tender_pq_criteria_1 = [
    {
        "description": "Форма випуску",
        "id": "400496-0001",
        "source": "tenderer",
        "classification": {"scheme": " espd211", "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES1"},
        "legislation": [
            {
                "version": "2020-04-19",
                "identifier": {
                    "id": "922-VIII",
                    "legalName": "Закон України \"Про публічні закупівлі\"",
                    "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                },
                "type": "NATIONAL_LEGISLATION",
            }
        ],
        "requirementGroups": [
            {
                "description": "Форма випуску",
                "id": "400496-0001-001",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": "Розчин для інфузій",
                        "id": "400496-0001-001-01",
                        "title": "Форма випуску",
                    }
                ],
            }
        ],
        "title": "Форма випуску",
    },
    {
        "description": "Доза діючої речовини",
        "id": "400496-0002",
        "source": "tenderer",
        "classification": {"scheme": " espd211", "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES2"},
        "legislation": [
            {
                "version": "2020-04-19",
                "identifier": {
                    "id": "922-VIII",
                    "legalName": "Закон України \"Про публічні закупівлі\"",
                    "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                },
                "type": "NATIONAL_LEGISLATION",
            }
        ],
        "requirementGroups": [
            {
                "description": "Доза діючої речовини",
                "id": "400496-0002-001",
                "requirements": [
                    {
                        "dataType": "integer",
                        "minValue": 5,
                        "id": "400496-0002-001-01",
                        "title": "Доза діючої речовини",
                        "unit": {"code": "KGM", "name": "кілограми"},
                    }
                ],
            }
        ],
        "title": "Доза діючої речовини",
    },
    {
        "description": "Форма випуску",
        "id": "400496-0003",
        "source": "tenderer",
        "classification": {"scheme": " espd211", "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES3"},
        "legislation": [
            {
                "version": "2020-04-19",
                "identifier": {
                    "id": "922-VIII",
                    "legalName": "Закон України \"Про публічні закупівлі\"",
                    "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                },
                "type": "NATIONAL_LEGISLATION",
            }
        ],
        "requirementGroups": [
            {
                "description": "Форма випуску",
                "id": "400496-0003-001",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValues": ["Відповідь1", "Відповідь2", "Відповідь3", "Відповідь4"],
                        "expectedMinItems": 2,
                        "expectedMaxItems": 3,
                        "id": "400496-0003-001-01",
                        "title": "Форма випуску",
                    }
                ],
            }
        ],
        "title": "Форма випуску",
    },
]

test_tender_pq_criteria_2 = [
    {
        "description": "Форма випуску",
        "id": "400496-0001",
        "source": "tenderer",
        "classification": {"scheme": " espd211", "id": "CRITERION.OTHER"},
        "legislation": [
            {
                "version": "2020-04-19",
                "identifier": {
                    "id": "922-VIII",
                    "legalName": "Закон України \"Про публічні закупівлі\"",
                    "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                },
                "type": "NATIONAL_LEGISLATION",
            }
        ],
        "requirementGroups": [
            {
                "description": "Форма випуску",
                "id": "400496-0001-001",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": "Розчин",
                        "id": "400496-0001-001-01",
                        "title": "Форма випуску",
                    }
                ],
            },
            {
                "description": "Форма випуску",
                "id": "400496-0001-002",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": "Порошок",
                        "id": "400496-0001-002-01",
                        "title": "Форма випуску",
                    }
                ],
            },
        ],
        "title": "Форма випуску",
    }
]


test_tender_pq_criteria_3 = [
    {
        "description": "Форма випуску",
        "id": "400496-0001",
        "source": "tenderer",
        "classification": {"scheme": " espd211", "id": "CRITERION.OTHER"},
        "legislation": [
            {
                "version": "2020-04-19",
                "identifier": {
                    "id": "922-VIII",
                    "legalName": "Закон України \"Про публічні закупівлі\"",
                    "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                },
                "type": "NATIONAL_LEGISLATION",
            }
        ],
        "requirementGroups": [
            {
                "description": "Форма випуску",
                "id": "400496-0001-001",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": "Розчин",
                        "id": "400496-0001-001-01",
                        "title": "Форма випуску",
                    },
                    {
                        "dataType": "integer",
                        "expectedValue": 500,
                        "id": "400496-0001-001-02",
                        "title": "Форма випуску",
                        "unit": {"code": "MLT", "name": "мл"},
                    },
                ],
            },
            {
                "description": "Форма випуску",
                "id": "400496-0001-002",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": "Порошок",
                        "id": "400496-0001-002-01",
                        "title": "Форма випуску",
                    }
                ],
            },
        ],
        "title": "Форма випуску",
    }
]


test_tender_pq_criteria_4 = [
    {
        "description": "Форма випуску",
        "title": "Форма випуску",
        "id": "400496-0001",
        "source": "tenderer",
        "classification": {"scheme": " espd211", "id": "CRITERION.OTHER"},
        "legislation": [
            {
                "version": "2020-04-19",
                "identifier": {
                    "id": "922-VIII",
                    "legalName": "Закон України \"Про публічні закупівлі\"",
                    "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                },
                "type": "NATIONAL_LEGISLATION",
            }
        ],
        "requirementGroups": [
            {
                "description": "Форма випуску",
                "id": "400496-0001-001",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValue": "Розчин",
                        "id": "400496-0001-001-01",
                        "title": "Форма випуску",
                    },
                    {
                        "dataType": "integer",
                        "expectedValue": 500,
                        "id": "400496-0001-001-02",
                        "title": "Форма випуску",
                        "unit": {"code": "MLT", "name": "мл"},
                    },
                    {
                        "dataType": "integer",
                        "expectedValue": 1,
                        "id": "400496-0001-001-03",
                        "title": "Форма випуску",
                        "unit": {"code": "H87", "name": "ШТ"},
                    },
                ],
            }
        ],
    }
]

test_tender_pq_response_1 = [
    {"requirement": {"id": "400496-0001-001-01"}, "value": "Розчин для інфузій"},
    {"requirement": {"id": "400496-0002-001-01"}, "value": 5},
    {"requirement": {"id": "400496-0003-001-01"}, "values": ["Відповідь1", "Відповідь2"]},
]


test_tender_pq_response_2 = [
    {"requirement": {"id": "400496-0001-001-01"}, "value": "Розчин"},
    {"requirement": {"id": "400496-0001-002-01"}, "value": "Порошок"},
]


test_tender_pq_response_3 = [
    {"requirement": {"id": "400496-0001-001-01"}, "value": "Розчин"},
    {"requirement": {"id": "400496-0001-001-02"}, "value": 500},
    {"requirement": {"id": "400496-0001-002-01"}, "value": "Порошок"},
]


test_tender_pq_response_4 = [
    {"requirement": {"id": "400496-0001-001-01"}, "value": "Порошок"},
    {"requirement": {"id": "400496-0001-001-02"}, "value": 500},
    {"requirement": {"id": "400496-0001-001-03"}, "value": 1},
]

test_tender_pq_response_5 = [{}]
