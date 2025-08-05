import os
from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.tests.base import BaseWebTest, test_signer_info
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.constants import MIN_BIDS_NUMBER
from openprocurement.tender.belowthreshold.tests.periods import PERIODS
from openprocurement.tender.core.tests.base import (
    BaseCoreWebTest,
    get_criteria_by_ids,
    test_criteria_all,
)
from openprocurement.tender.core.tests.utils import set_tender_multi_buyers

now = get_now()

test_tender_below_identifier = {
    "scheme": "UA-IPN",
    "id": "00037256",
    "uri": "http://www.dus.gov.ua/",
    "legalName": "Державне управління справами",
}

test_tender_below_base_organization = {
    "name": "Державне управління справами",
    "identifier": test_tender_below_identifier,
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
}

test_tender_below_organization = test_tender_below_base_organization.copy()
test_tender_below_organization["scale"] = "micro"

test_tender_below_supplier = test_tender_below_organization.copy()
test_tender_below_supplier["signerInfo"] = test_signer_info

test_tender_below_author = test_tender_below_base_organization.copy()

test_tender_below_procuring_entity = test_tender_below_base_organization.copy()
test_tender_below_procuring_entity["kind"] = "general"
test_tender_below_procuring_entity["signerInfo"] = test_signer_info

test_tender_below_buyer = test_tender_below_procuring_entity.copy()
test_tender_below_buyer.pop("contactPoint")

test_tender_below_milestones = [
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

test_tender_below_item = {
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

test_tender_below_data = {
    "title": "футляри до державних нагород",
    "mainProcurementCategory": "goods",
    "procuringEntity": test_tender_below_procuring_entity,
    "value": {"amount": 500, "currency": "UAH"},
    "items": [deepcopy(test_tender_below_item)],
    "enquiryPeriod": {"endDate": (now + timedelta(days=9)).isoformat()},
    "tenderPeriod": {"endDate": (now + timedelta(days=18)).isoformat()},
    "procurementMethodType": "belowThreshold",
    "milestones": test_tender_below_milestones,
    "contractTemplateName": "00000000.0002.01",
}

funder = deepcopy(test_tender_below_base_organization)
funder["identifier"]["id"] = "44000"
funder["identifier"]["scheme"] = "XM-DAC"

test_tender_below_with_inspector_data = deepcopy(test_tender_below_data)
test_tender_below_with_inspector_data.update({"funders": [funder], "inspector": funder})

if SANDBOX_MODE:
    test_tender_below_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_below_data_no_auction = deepcopy(test_tender_below_data)
test_tender_below_data_no_auction["funders"] = [deepcopy(test_tender_below_base_organization)]
test_tender_below_data_no_auction["funders"][0]["identifier"]["id"] = "44000"
test_tender_below_data_no_auction["funders"][0]["identifier"]["scheme"] = "XM-DAC"

test_tender_below_simple_data = deepcopy(test_tender_below_data)
test_tender_below_simple_data["procurementMethodRationale"] = "simple"

test_tender_below_features_data = test_tender_below_data.copy()
test_tender_below_features_item = test_tender_below_features_data["items"][0].copy()
test_tender_below_features_item["id"] = uuid4().hex
test_tender_below_features_data["items"] = [test_tender_below_features_item]
test_tender_below_features_data["features"] = [
    {
        "code": "OCDS-123454-AIR-INTAKE",
        "featureOf": "item",
        "relatedItem": test_tender_below_features_item["id"],
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
test_tender_below_bids = [
    {
        "tenderers": [deepcopy(test_tender_below_supplier)],
        "value": {"amount": 469.0, "currency": "UAH", "valueAddedTaxIncluded": True},
    },
    {
        "tenderers": [deepcopy(test_tender_below_supplier)],
        "value": {"amount": 479.0, "currency": "UAH", "valueAddedTaxIncluded": True},
    },
]
test_tender_below_lots = [
    {
        "title": "lot title",
        "description": "lot description",
        "value": test_tender_below_data["value"],
        "minimalStep": {"amount": 15, "currency": "UAH"},
    }
]
test_tender_below_lots_no_min_step = [
    {
        "title": "lot title",
        "description": "lot description",
        "value": test_tender_below_data["value"],
    }
]
test_tender_below_cancellation = {
    "reason": "cancellation reason",
}
if RELEASE_2020_04_19 < get_now():
    test_tender_below_cancellation.update({"reasonType": "noDemand"})

test_tender_below_draft_claim = {
    "title": "complaint title",
    "status": "draft",
    "type": "claim",
    "description": "complaint description",
    "author": test_tender_below_author,
}

test_tender_below_claim = {
    "title": "complaint title",
    "status": "claim",
    "type": "claim",
    "description": "complaint description",
    "author": test_tender_below_author,
}

test_tender_below_complaint = {
    "title": "complaint title",
    "status": "pending",
    "type": "complaint",
    "description": "complaint description",
    "author": test_tender_below_author,
}

test_tender_below_draft_complaint = {
    "title": "complaint title",
    "type": "complaint",
    "description": "complaint description",
    "author": test_tender_below_author,
}

test_tender_below_multi_buyers_data = set_tender_multi_buyers(
    test_tender_below_data,
    test_tender_below_item,
    test_tender_below_buyer,
)

test_tender_below_config = {
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
    "clarificationUntilDuration": 1,
    "qualificationDuration": 0,
    "restricted": False,
}

test_tender_below_required_criteria_ids = set()

test_tender_below_criteria = []
test_tender_below_criteria.extend(get_criteria_by_ids(test_criteria_all, test_tender_below_required_criteria_ids))


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_below_data
    initial_config = test_tender_below_config
    initial_status = "active.enquiries"
    initial_bids = None
    initial_lots = None
    initial_criteria = None
    tender_for_funders = False
    initial_auth = ("Basic", ("broker", ""))
    min_bids_number = MIN_BIDS_NUMBER
    # Statuses for test, that will be imported from others procedures
    primary_tender_status = "active.enquiries"  # status, to which tender should be switched from 'draft'
    forbidden_document_modification_actions_status = (
        "active.tendering"  # status, in which operations with tender documents (adding, updating) are forbidden
    )
    forbidden_question_add_actions_status = "active.tendering"  # status, in which adding tender questions is forbidden
    forbidden_question_update_actions_status = (
        "active.auction"  # status, in which updating tender questions is forbidden
    )
    forbidden_lot_actions_status = (
        "active.tendering"  # status, in which operations with tender lots (adding, updating, deleting) are forbidden
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


class TenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_below_data
    initial_config = test_tender_below_config
    initial_status = "active.enquiries"
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super().setUp()
        self.create_tender()
