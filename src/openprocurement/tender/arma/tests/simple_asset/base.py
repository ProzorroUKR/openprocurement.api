import copy
import os

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.constants_env import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now
from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.tender.arma.constants import SIMPLE_ASSET_ARMA
from openprocurement.tender.arma.tests.complex_asset.base import (
    test_tender_arma_data,
    test_tender_arma_procuring_entity,
    test_tender_arma_supplier,
)
from openprocurement.tender.arma.tests.simple_asset.periods import PERIODS
from openprocurement.tender.core.tests.base import (
    get_criteria_by_ids,
    test_article_16_criteria,
    test_criteria_all,
)
from openprocurement.tender.core.tests.utils import change_auth, set_tender_periods
from openprocurement.tender.open.tests.above_threshold_ua.base import BaseTenderUAWebTest

now = get_now()

test_tender_arma_simple_supplier = copy.deepcopy(test_tender_arma_supplier)
test_tender_arma_simple_procuring_entity = copy.deepcopy(test_tender_arma_procuring_entity)

test_tender_arma_simple_bids = [
    {
        "tenderers": [copy.deepcopy(test_tender_arma_simple_supplier)],
        "value": {"amountPercentage": 38},
    },
    {
        "tenderers": [copy.deepcopy(test_tender_arma_simple_supplier)],
        "value": {"amountPercentage": 39},
    },
]

for bid in test_tender_arma_simple_bids:
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        bid["selfEligible"] = True

test_tender_arma_simple_three_bids = copy.deepcopy(test_tender_arma_simple_bids)
test_tender_arma_simple_three_bids.append(
    {
        "tenderers": [copy.deepcopy(test_tender_arma_simple_supplier)],
        "value": {"amountPercentage": 50},
    }
)
for bid in test_tender_arma_simple_three_bids:
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        bid["selfEligible"] = True

test_tender_arma_simple_data = copy.deepcopy(test_tender_arma_data)
test_tender_arma_simple_data["procurementMethodType"] = SIMPLE_ASSET_ARMA
test_tender_arma_simple_data.pop("enquiryPeriod", None)
set_tender_periods(test_tender_arma_simple_data, start=now)
if SANDBOX_MODE:
    test_tender_arma_simple_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_arma_simple_lots = [
    {
        "title": "lot title",
        "description": "lot description",
        "value": {"amountPercentage": 50},
        "minimalStep": {"amountPercentage": 1},
        "minExpectedIncome": {"amount": 100000.00, "currency": "UAH", "valueAddedTaxIncluded": True},
    }
]

test_tender_arma_simple_config = {
    "hasAuction": True,
    "hasAwardingOrder": True,
    "hasValueRestriction": False,
    "valueCurrencyEquality": True,
    "hasPrequalification": False,
    "minBidsNumber": 2,
    "hasPreSelectionAgreement": True,
    "hasTenderComplaints": False,
    "hasAwardComplaints": False,
    "hasCancellationComplaints": False,
    "hasValueEstimation": False,
    "hasQualificationComplaints": False,
    "tenderComplainRegulation": 0,
    "qualificationComplainDuration": 0,
    "awardComplainDuration": 0,
    "cancellationComplainDuration": 0,
    "clarificationUntilDuration": 0,
    "qualificationDuration": 0,
    "minTenderingDuration": 10,
    "hasEnquiries": False,
    "minEnquiriesDuration": 0,
    "enquiryPeriodRegulation": 0,
    "restricted": False,
    "hasMultiSourcing": False,
}

test_tender_arma_simple_required_criteria_ids = {}
test_tender_arma_simple_criteria = []
test_tender_arma_simple_criteria.extend(
    get_criteria_by_ids(test_criteria_all, test_tender_arma_simple_required_criteria_ids)
)
test_tender_arma_simple_criteria.extend(test_article_16_criteria[:1])

test_agreement_arma_contract_raw_data = {
    "status": "active",
    "suppliers": [copy.deepcopy(test_tender_arma_simple_supplier)],
}

test_agreement_arma_data = {
    "_id": "6b9b3b4a3b1c4a2e8f0d5c7a9e1b2d4f",
    "doc_type": "Agreement",
    "agreementID": "UA-2025-01-15-000001",
    "agreementType": ARMA_TYPE,
    "status": "active",
    "frameworkID": "985a2e3eab47427283a5c51e84d0986d",
    "period": {
        "startDate": "2025-01-15T00:00:00.318051+02:00",
        "endDate": "2027-01-15T00:00:00.318051+02:00",
    },
    "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
    "procuringEntity": copy.deepcopy(test_tender_arma_simple_procuring_entity),
    "contracts": [
        copy.deepcopy(test_agreement_arma_contract_raw_data),
        copy.deepcopy(test_agreement_arma_contract_raw_data),
    ],
}


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderSimpleAssetWebTest(BaseTenderUAWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_arma_simple_data
    initial_config = test_tender_arma_simple_config
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None
    initial_criteria = None
    initial_auth = None

    initial_agreement_data = test_agreement_arma_data
    agreement_id = initial_agreement_data["_id"]

    enquiry_period_allowed = False
    periods = PERIODS

    def setUp(self):
        super(BaseTenderUAWebTest, self).setUp()
        self.app.authorization = self.initial_auth or ("Basic", ("broker", ""))
        self.create_agreement()
        self.initial_data["agreement"] = {"id": self.agreement_id}

    def tearDown(self):
        self.delete_agreement()
        super().tearDown()

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", startend="enquiry_end")

    def set_complaint_period_end(self):
        self.set_status("active.tendering", startend="complaint_end")

    def prepare_award(self):
        self.set_status("active.auction", {"id": self.tender_id, "status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.auction")

        with change_auth(self.app, ("Basic", ("auction", ""))):
            response = self.app.get("/tenders/{}/auction".format(self.tender_id))
            auction_bids_data = response.json["data"]["bids"]
            for lot_id in self.initial_lots:
                response = self.app.post_json(
                    "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]),
                    {
                        "data": {
                            "bids": [
                                {
                                    "id": b["id"],
                                    "lotValues": [
                                        {
                                            "relatedLot": lot["relatedLot"],
                                            "value": lot["value"],
                                        }
                                        for lot in b["lotValues"]
                                    ],
                                }
                                for b in auction_bids_data
                            ]
                        }
                    },
                )
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.content_type, "application/json")
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "active.qualification")


class BaseTenderSimpleAssetContentWebTest(BaseTenderSimpleAssetWebTest):
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super().setUp()
        self.create_tender()
