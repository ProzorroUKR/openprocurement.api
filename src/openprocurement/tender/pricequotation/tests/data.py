from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.tests.base import test_signer_info
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.base import (
    get_criteria_by_ids,
    test_criteria_all,
    test_tech_feature_criteria,
)
from openprocurement.tender.core.tests.utils import set_tender_multi_buyers
from openprocurement.tender.pricequotation.constants import PQ

now = get_now()

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

test_tender_pq_base_organization = {
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
}

test_tender_pq_organization = test_tender_pq_base_organization.copy()
test_tender_pq_organization["scale"] = "micro"

test_tender_pq_supplier = test_tender_pq_organization.copy()
test_tender_pq_supplier["signerInfo"] = test_signer_info

test_tender_pq_author = test_tender_pq_base_organization.copy()

test_tender_pq_procuring_entity = test_tender_pq_base_organization.copy()
test_tender_pq_procuring_entity["kind"] = "general"
test_tender_pq_procuring_entity["signerInfo"] = test_signer_info

test_tender_pq_buyer = test_tender_pq_procuring_entity.copy()
test_tender_pq_buyer.pop("contactPoint")

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
        "value": {"amount": 100},
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
    "contractTemplateName": "00000000-0.0002.01",
}

if SANDBOX_MODE:
    test_tender_pq_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_pq_multi_buyers_data = set_tender_multi_buyers(
    test_tender_pq_data,
    test_tender_pq_data["items"][0],
    test_tender_pq_buyer,
)

test_tender_pq_bids = [
    {
        "tenderers": [test_tender_pq_supplier],
        "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
    },
    {
        "tenderers": [test_tender_pq_supplier],
        "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True},
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

test_tech_features_requirements = [
    {
        "title": "Діагональ екрану",
        "dataType": "number",
        "minValue": 23.8,
        "unit": {"code": "INH", "name": "дюйм"},
    },
    {
        "title": "Роздільна здатність",
        "dataType": "string",
        "expectedValues": ["1920x1080"],
        "expectedMinItems": 1,
    },
    {
        "title": "Співвідношення сторін",
        "dataType": "string",
        "expectedValues": ["16:9"],
        "expectedMinItems": 1,
    },
    {
        "title": "Яскравість дисплея",
        "dataType": "integer",
        "minValue": 0,
        "maxValue": 250,
        "unit": {"code": "A24", "name": "кд/м²"},
    },
    {
        "title": "Контрастність (статична)",
        "dataType": "string",
        "expectedValues": ["1000:1"],
        "expectedMinItems": 1,
    },
    {
        "title": "Кількість портів HDMI",
        "dataType": "integer",
        "minValue": 1,
        "unit": {"code": "H87", "name": "штук"},
    },
    {
        "title": "Кількість портів D-sub",
        "dataType": "integer",
        "minValue": 1,
        "unit": {"code": "H87", "name": "штук"},
    },
    {
        "title": "Кабель для під’єднання",
        "dataType": "string",
        "expectedValues": ["HDMI"],
        "expectedMinItems": 1,
    },
    {
        "title": "Гарантія",
        "dataType": "integer",
        "minValue": 36,
        "unit": {"code": "MON", "name": "місяців"},
    },
]

test_tender_pq_required_criteria_ids = {
    "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES",
}

test_tender_pq_criteria = []
test_tender_pq_criteria.extend(get_criteria_by_ids(test_criteria_all, test_tender_pq_required_criteria_ids))

for criterion in test_tender_pq_criteria:
    if criterion["classification"]["id"] == "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES":
        criterion["requirementGroups"][0]["requirements"] = deepcopy(test_tech_features_requirements)

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

test_profile_tech_features_criteria = deepcopy(test_tech_feature_criteria)
test_profile_tech_features_criteria[0].pop("relatesTo", None)
test_profile_tech_features_criteria[0].pop("relatedItem", None)
test_profile_tech_features_criteria[0]["requirementGroups"][0]["requirements"] = deepcopy(
    test_tech_features_requirements
)

test_tender_pq_short_profile = {
    "classification": {"description": "Комп’ютерне обладнання", "id": "30230000-0", "scheme": "ДК021"},
    "id": "655360-30230000-889652-40000777",
    "relatedCategory": "655360-30230000-889652",
    "unit": {"code": "H87", "name": "штук"},
    "criteria": deepcopy(test_profile_tech_features_criteria),
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

test_bid_pq_product = {
    "status": "active",
}

test_tender_pq_criteria_1 = [
    {
        "description": "Форма випуску",
        "id": "400496-0001",
        "source": "tenderer",
        "relatesTo": "item",
        "classification": {"scheme": "ESPD211", "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES"},
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
                        "expectedValues": ["Розчин для інфузій"],
                        "id": "400496-0001-001-01",
                        "title": "Форма випуску",
                        "expectedMinItems": 1,
                    },
                    {
                        "dataType": "integer",
                        "minValue": 5,
                        "id": "400496-0002-001-02",
                        "title": "Доза діючої речовини",
                        "unit": {"code": "KGM", "name": "кілограми"},
                    },
                    {
                        "dataType": "string",
                        "expectedValues": ["Відповідь1", "Відповідь2", "Відповідь3", "Відповідь4"],
                        "expectedMinItems": 1,
                        "expectedMaxItems": 3,
                        "id": "400496-0003-001-03",
                        "title": "Форма випуску 1",
                    },
                ],
            },
        ],
        "title": "Форма випуску",
    },
]

test_tender_pq_criteria_2 = [
    {
        "description": "Форма випуску",
        "id": "400496-0001",
        "source": "tenderer",
        "relatesTo": "item",
        "classification": {"scheme": "ESPD211", "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES"},
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
                        "expectedValues": ["Розчин"],
                        "id": "400496-0001-001-01",
                        "title": "Форма випуску",
                        "expectedMinItems": 1,
                    }
                ],
            },
            {
                "description": "Форма випуску",
                "id": "400496-0001-002",
                "requirements": [
                    {
                        "dataType": "string",
                        "expectedValues": ["Порошок"],
                        "id": "400496-0001-002-01",
                        "title": "Форма випуску",
                        "expectedMinItems": 1,
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
        "relatesTo": "item",
        "classification": {"scheme": "ESPD211", "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES"},
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
                        "expectedValues": ["Розчин"],
                        "id": "400496-0001-001-01",
                        "title": "Форма випуску",
                        "expectedMinItems": 1,
                    },
                    {
                        "dataType": "integer",
                        "expectedValue": 500,
                        "id": "400496-0001-001-02",
                        "title": "Форма випуску 2",
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
                        "expectedValues": ["Порошок"],
                        "id": "400496-0001-002-01",
                        "title": "Форма випуску",
                        "expectedMinItems": 1,
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
        "relatesTo": "item",
        "classification": {"scheme": "ESPD211", "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES"},
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
                        "expectedValues": ["Розчин"],
                        "expectedMinItems": 1,
                        "id": "400496-0001-001-01",
                        "title": "Форма випуску",
                    },
                    {
                        "dataType": "integer",
                        "expectedValue": 500,
                        "id": "400496-0001-001-02",
                        "title": "Форма випуску 2",
                        "unit": {"code": "MLT", "name": "мл"},
                    },
                    {
                        "dataType": "integer",
                        "expectedValue": 1,
                        "id": "400496-0001-001-03",
                        "title": "Форма випуску 3",
                        "unit": {"code": "H87", "name": "ШТ"},
                    },
                ],
            }
        ],
    }
]

test_tender_pq_response_1 = [
    {"requirement": {"id": "400496-0001-001-01"}, "values": ["Розчин для інфузій"]},
    {"requirement": {"id": "400496-0002-001-02"}, "value": 5},
    {"requirement": {"id": "400496-0003-001-03"}, "values": ["Відповідь1", "Відповідь2"]},
]


test_tender_pq_response_2 = [
    {"requirement": {"id": "400496-0001-001-01"}, "values": ["Розчин"]},
    {"requirement": {"id": "400496-0001-002-01"}, "values": ["Порошок"]},
]


test_tender_pq_response_3 = [
    {"requirement": {"id": "400496-0001-001-01"}, "values": ["Розчин"]},
    {"requirement": {"id": "400496-0001-001-02"}, "value": 500},
    {"requirement": {"id": "400496-0001-002-01"}, "values": ["Порошок"]},
]


test_tender_pq_response_4 = [
    {"requirement": {"id": "400496-0001-001-01"}, "values": ["Порошок"]},
    {"requirement": {"id": "400496-0001-001-02"}, "value": 500},
    {"requirement": {"id": "400496-0001-001-03"}, "value": 1},
]

test_tender_pq_response_5 = [{}]

test_agreement_contracts_data = [
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
]

test_agreement_pq_data = {
    "_id": "2e14a78a2074952d5a2d256c3c004dda",
    "doc_type": "Agreement",
    "agreementID": "UA-2021-11-12-000001",
    "agreementType": "electronicCatalogue",
    "frameworkID": "985a2e3eab47427283a5c51e84d0986d",
    "period": {"startDate": "2021-11-12T00:00:00.318051+02:00", "endDate": "2022-02-24T20:14:24.577158+03:00"},
    "status": "active",
    "contracts": test_agreement_contracts_data,
    "procuringEntity": test_tender_pq_procuring_entity,
}
