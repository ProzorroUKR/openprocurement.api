import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.base import (
    BaseCoreWebTest,
    get_criteria_by_ids,
    test_criteria_all,
)
from openprocurement.tender.core.tests.utils import (
    set_bid_lotvalues,
    set_tender_criteria,
    set_tender_lots,
    set_tender_multi_buyers,
)
from openprocurement.tender.requestforproposal.constants import MIN_BIDS_NUMBER
from openprocurement.tender.requestforproposal.tests.periods import PERIODS

now = get_now()

test_tender_rfp_identifier = {
    "scheme": "UA-IPN",
    "id": "00037256",
    "uri": "http://www.dus.gov.ua/",
    "legalName": "Державне управління справами",
}

test_tender_rfp_organization = {
    "name": "Державне управління справами",
    "identifier": test_tender_rfp_identifier,
    "address": {
        "countryName": "Україна",
        "postalCode": "01220",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова, 11, корпус 1",
    },
    "contactPoint": {
        "name": "Державне управління справами",
        "telephone": "+0440000000",
    },
    "scale": "micro",
}

test_tender_rfp_author = test_tender_rfp_organization.copy()
del test_tender_rfp_author["scale"]

test_tender_rfp_procuring_entity = test_tender_rfp_author.copy()
test_tender_rfp_procuring_entity["kind"] = "general"

test_agreement_rfp_data = {
    "_id": "2e14a78a2074952d5a2d256c3c004dda",
    "doc_type": "Agreement",
    "agreementID": "UA-2021-11-12-000001",
    "agreementType": "internationalFinancialInstitutions",
    "frameworkID": "985a2e3eab47427283a5c51e84d0986d",
    "period": {"startDate": "2021-11-12T00:00:00.318051+02:00", "endDate": "2022-02-24T20:14:24.577158+03:00"},
    "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
    "status": "active",
    "procuringEntity": test_tender_rfp_procuring_entity,
    "contracts": [
        {
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
                        "scheme": "UA-EDR",
                    },
                    "name": "Товариство з обмеженою відповідальністю «Пікселі»",
                    "scale": "large",
                }
            ],
        },
        {
            "status": "suspended",
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
                        "scheme": "UA-EDR",
                    },
                    "name": "Товариство з обмеженою відповідальністю «Штекер-Пекер»",
                    "scale": "large",
                }
            ],
        },
    ],
}

test_tender_rfp_milestones = [
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

test_tender_rfp_item = {
    "description": "футляри до державних нагород",
    "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
    "additionalClassifications": [
        {"scheme": "ДКПП", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"}
    ],
    "unit": {
        "name": "кг",
        "code": "KGM",
        "value": {"amount": 6},
    },
    "quantity": 5,
    "deliveryDate": {
        "startDate": (now + timedelta(days=2)).isoformat(),
        "endDate": (now + timedelta(days=5)).isoformat(),
    },
    "deliveryAddress": {
        "countryName": "Україна",
        "postalCode": "79000",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова 1",
    },
}

funder = deepcopy(test_tender_rfp_organization)
del funder["scale"]
funder["identifier"]["id"] = "44000"
funder["identifier"]["scheme"] = "XM-DAC"

test_tender_rfp_data = {
    "title": "футляри до державних нагород",
    "mainProcurementCategory": "goods",
    "procuringEntity": test_tender_rfp_procuring_entity,
    "value": {"amount": 500, "currency": "UAH"},
    "minimalStep": {"amount": 15, "currency": "UAH"},
    "items": [deepcopy(test_tender_rfp_item)],
    "enquiryPeriod": {"endDate": (now + timedelta(days=9)).isoformat()},
    "tenderPeriod": {"endDate": (now + timedelta(days=18)).isoformat()},
    "procurementMethodType": "requestForProposal",
    "milestones": test_tender_rfp_milestones,
    "funders": [funder],
    "contractTemplateName": "00000000-0.0002.01",
}

test_tender_rfp_with_inspector_data = deepcopy(test_tender_rfp_data)
test_tender_rfp_with_inspector_data.update({"funders": [funder], "inspector": funder})

if SANDBOX_MODE:
    test_tender_rfp_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_rfp_data_no_auction = deepcopy(test_tender_rfp_data)
del test_tender_rfp_data_no_auction["minimalStep"]
test_tender_rfp_data_no_auction["funders"] = [deepcopy(test_tender_rfp_organization)]
test_tender_rfp_data_no_auction["funders"][0]["identifier"]["id"] = "44000"
test_tender_rfp_data_no_auction["funders"][0]["identifier"]["scheme"] = "XM-DAC"
del test_tender_rfp_data_no_auction["funders"][0]["scale"]

test_tender_rfp_simple_data = deepcopy(test_tender_rfp_data)
test_tender_rfp_simple_data["procurementMethodRationale"] = "simple"

test_tender_rfp_features_data = test_tender_rfp_data.copy()
test_tender_rfp_features_item = test_tender_rfp_features_data["items"][0].copy()
test_tender_rfp_features_item["id"] = "1"
test_tender_rfp_features_data["items"] = [test_tender_rfp_features_item]
test_tender_rfp_features_data["features"] = [
    {
        "code": "OCDS-123454-AIR-INTAKE",
        "featureOf": "item",
        "relatedItem": "1",
        "title": "Потужність всмоктування",
        "title_en": "Air Intake",
        "description": "Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
        "enum": [{"value": 0.1, "title": "До 1000 Вт"}, {"value": 0.15, "title": "Більше 1000 Вт"}],
    },
    {
        "code": "OCDS-123454-YEARS",
        "featureOf": "tenderer",
        "title": "Років на ринку",
        "title_en": "Years trading",
        "description": "Кількість років, які організація учасник працює на ринку",
        "enum": [
            {"value": 0.05, "title": "До 3 років"},
            {"value": 0.1, "title": "Більше 3 років, менше 5 років"},
            {"value": 0.15, "title": "Більше 5 років"},
        ],
    },
]
test_tender_rfp_bids = [
    {
        "tenderers": [test_tender_rfp_organization],
        "value": {"amount": 469.0, "currency": "UAH", "valueAddedTaxIncluded": True},
    },
    {
        "tenderers": [test_tender_rfp_organization],
        "value": {"amount": 479.0, "currency": "UAH", "valueAddedTaxIncluded": True},
    },
]
test_tender_rfp_lots = [
    {
        "title": "lot title",
        "description": "lot description",
        "value": test_tender_rfp_data["value"],
        "minimalStep": test_tender_rfp_data["minimalStep"],
    }
]
test_tender_rfp_lots_no_min_step = [
    {
        "title": "lot title",
        "description": "lot description",
        "value": test_tender_rfp_data["value"],
    }
]
test_tender_rfp_cancellation = {
    "reason": "cancellation reason",
}
if RELEASE_2020_04_19 < get_now():
    test_tender_rfp_cancellation.update({"reasonType": "noDemand"})

test_tender_rfp_draft_claim = {
    "title": "complaint title",
    "status": "draft",
    "type": "claim",
    "description": "complaint description",
    "author": test_tender_rfp_author,
}

test_tender_rfp_claim = {
    "title": "complaint title",
    "status": "claim",
    "type": "claim",
    "description": "complaint description",
    "author": test_tender_rfp_author,
}

test_tender_rfp_complaint = {
    "title": "complaint title",
    "status": "pending",
    "type": "complaint",
    "description": "complaint description",
    "author": test_tender_rfp_author,
}

test_tender_rfp_draft_complaint = {
    "title": "complaint title",
    "type": "complaint",
    "description": "complaint description",
    "author": test_tender_rfp_author,
}

test_tender_rfp_multi_buyers_data = set_tender_multi_buyers(
    test_tender_rfp_data,
    test_tender_rfp_item,
    test_tender_rfp_organization,
)

test_tender_rfp_config = {
    "hasAuction": True,
    "hasAwardingOrder": True,
    "hasValueRestriction": True,
    "valueCurrencyEquality": True,
    "hasPrequalification": False,
    "minBidsNumber": 1,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": False,
    "hasAwardComplaints": False,
    "hasCancellationComplaints": False,
    "hasValueEstimation": True,
    "hasQualificationComplaints": False,
    "tenderComplainRegulation": 0,
    "qualificationComplainDuration": 0,
    "awardComplainDuration": 2,
    "cancellationComplainDuration": 0,
    "clarificationUntilDuration": 4,
    "qualificationDuration": 20,
    "restricted": False,
}

test_tender_rfp_required_criteria_ids = set()

test_tender_rfp_allowed_criteria_ids = {
    "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION",
    "CRITERION.EXCLUSION.CONVICTIONS.FRAUD",
    "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION",
    "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING",
    "CRITERION.EXCLUSION.CONVICTIONS.TERRORIST_OFFENCES",
    "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.EARLY_TERMINATION",
    "CRITERION.EXCLUSION.CONTRIBUTIONS.PAYMENT_OF_TAXES",
    "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY",
    "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION",
    "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION",
    "CRITERION.EXCLUSION.NATIONAL.OTHER",
    "CRITERION.OTHER.BID.LANGUAGE",
}

test_tender_rfp_criteria = []
test_tender_rfp_criteria.extend(get_criteria_by_ids(test_criteria_all, test_tender_rfp_required_criteria_ids))
test_tender_rfp_criteria.extend(get_criteria_by_ids(test_criteria_all, test_tender_rfp_allowed_criteria_ids))


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_rfp_data
    initial_config = test_tender_rfp_config
    initial_status = "active.enquiries"
    initial_bids = None
    initial_lots = None
    initial_criteria = None
    tender_for_funders = True
    initial_auth = ("Basic", ("broker", ""))
    min_bids_number = MIN_BIDS_NUMBER
    # Statuses for test, that will be imported from others procedures
    primary_tender_status = "active.enquiries"  # status, to which tender should be switched from 'draft'
    forbidden_question_add_actions_status = "active.tendering"  # status, in which adding tender questions is forbidden
    forbidden_question_update_actions_status = (
        "active.auction"  # status, in which updating tender questions is forbidden
    )
    forbidden_lot_actions_status = (
        "active.auction"  # status, in which operations with tender lots (adding, updating, deleting) are forbidden
    )
    forbidden_contract_document_modification_actions_status = (
        "unsuccessful"  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    )
    # auction role actions
    forbidden_auction_actions_status = "active.tendering"  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = (
        "active.tendering"  # status, in which adding document to tender auction is forbidden
    )

    periods = PERIODS
    guarantee_criterion = None

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", extra={"status": "active.enquires"})

    def setUp(self):
        super().setUp()
        self.initial_data = deepcopy(self.initial_data)
        self.initial_config = deepcopy(self.initial_config)
        if self.initial_lots:
            self.initial_lots = deepcopy(self.initial_lots)
            set_tender_lots(self.initial_data, self.initial_lots)
            self.initial_lots = self.initial_data["lots"]
        if self.initial_bids:
            self.initial_bids = deepcopy(self.initial_bids)
            for bid in self.initial_bids:
                if self.initial_lots:
                    set_bid_lotvalues(bid, self.initial_lots)
        if self.initial_criteria:
            self.initial_criteria = deepcopy(self.initial_criteria)
            self.initial_criteria = set_tender_criteria(
                self.initial_criteria,
                self.initial_data.get("lots", []),
                self.initial_data.get("items", []),
            )


class TenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_rfp_data
    initial_config = test_tender_rfp_config
    initial_status = "active.enquiries"
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super().setUp()
        if self.initial_agreement_data:
            self.create_agreement()
            self.initial_data["agreements"] = [{"id": self.agreement_id}]
        self.create_tender()
