import copy
import os
from datetime import datetime, timedelta

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.constants_env import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.tests.base import test_signer_info
from openprocurement.api.utils import get_now
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.tests.periods import PERIODS, TENDERING_DAYS
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_buyer,
    test_tender_below_milestones,
)
from openprocurement.tender.core.tests.base import (
    get_criteria_by_ids,
    test_article_16_criteria,
    test_criteria_all,
)
from openprocurement.tender.core.tests.utils import change_auth, set_tender_multi_buyers
from openprocurement.tender.openua.tests.base import BaseTenderUAWebTest

test_tender_arma_milestones = copy.deepcopy(test_tender_below_milestones)

test_tender_arma_supplier = {
    "name": "Державне управління справами",
    "name_en": "State administration",
    "identifier": {
        "legalName_en": "dus.gov.ua",
        "legalName": "Державне управління справами",
        "scheme": "UA-IPN",
        "id": "00037256",
        "uri": "http://www.dus.gov.ua/",
    },
    "address": {
        "countryName": "Україна",
        "postalCode": "01220",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова, 11, корпус 1",
    },
    "contactPoint": {
        "name": "Державне управління справами",
        "name_en": "State administration",
        "telephone": "+0440000000",
    },
    "scale": "micro",
    "signerInfo": test_signer_info,
}

test_tender_arma_bids = [
    {
        "tenderers": [copy.deepcopy(test_tender_arma_supplier)],
        "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
        "selfQualified": True,
    },
    {
        "tenderers": [copy.deepcopy(test_tender_arma_supplier)],
        "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True},
        "selfQualified": True,
    },
]

for bid in test_tender_arma_bids:
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        bid["selfEligible"] = True

test_tender_arma_three_bids = copy.deepcopy(test_tender_arma_bids)
test_tender_arma_three_bids.append(
    {
        "tenderers": [test_tender_arma_supplier.copy()],
        "value": {"amount": 489, "currency": "UAH", "valueAddedTaxIncluded": True},
        "selfQualified": True,
    }
)
for bid in test_tender_arma_three_bids:
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        bid["selfEligible"] = True

now = datetime.now()

test_tender_arma_procuring_entity = {
    "kind": "authority",
    "name": "Державне управління справами",
    "name_en": "State administration",
    "identifier": {
        "legalName_en": "dus.gov.ua",
        "scheme": "UA-EDR",
        "id": "00037256",
        "uri": "http://www.dus.gov.ua/",
    },
    "address": {
        "countryName": "Україна",
        "postalCode": "01220",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова, 11, корпус 1",
    },
    "contactPoint": {
        "name": "Державне управління справами",
        "name_en": "State administration",
        "telephone": "+0440000000",
    },
    "signerInfo": test_signer_info,
}

test_tender_arma_data = {
    "title": "футляри до державних нагород",
    "title_en": "Cases for state awards",
    "mainProcurementCategory": "services",
    "procuringEntity": test_tender_arma_procuring_entity.copy(),
    "value": {"currency": "UAH"},
    "items": [
        {
            "description": "футляри до державних нагород",
            "description_en": "Cases for state awards",
            "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
            "additionalClassifications": [
                {
                    "scheme": "ДКПП",
                    "id": "17.21.1",
                    "description": "папір і картон гофровані, паперова й картонна тара",
                }
            ],
            "unit": {"name": "item", "code": "KGM", "value": {"amount": 6}},
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
    ],
    "tenderPeriod": {"endDate": (now + timedelta(days=TENDERING_DAYS + 1)).isoformat()},
    "procurementMethodType": COMPLEX_ASSET_ARMA,
    "milestones": test_tender_arma_milestones,
}
if SANDBOX_MODE:
    test_tender_arma_data["procurementMethodDetails"] = "quick, accelerator=1440"


test_tender_arma_lots = [
    {
        "title": "lot title",
        "description": "lot description",
        "value": test_tender_arma_data["value"],
        "minimalStep": {"currency": "UAH"},
    }
]

test_tender_arma_multi_buyers_data = set_tender_multi_buyers(
    test_tender_arma_data,
    test_tender_arma_data["items"][0],
    test_tender_below_buyer,
)


test_tender_arma_config = {
    "hasAuction": True,
    "hasAwardingOrder": True,
    "hasValueRestriction": False,
    "valueCurrencyEquality": True,
    "hasPrequalification": True,
    "minBidsNumber": 2,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": False,
    "hasAwardComplaints": False,
    "hasCancellationComplaints": False,
    "hasValueEstimation": False,
    "hasQualificationComplaints": False,
    "tenderComplainRegulation": 0,
    "qualificationComplainDuration": 0,
    "awardComplainDuration": 0,
    "cancellationComplainDuration": 0,
    "clarificationUntilDuration": 5,
    "qualificationDuration": 10,
    "minTenderingDuration": 20,
    "hasEnquiries": False,
    "minEnquiriesDuration": 0,
    "enquiryPeriodRegulation": 10,
    "restricted": False,
}

test_tender_arma_required_criteria_ids = {}
test_tender_arma_criteria = []
test_tender_arma_criteria.extend(get_criteria_by_ids(test_criteria_all, test_tender_arma_required_criteria_ids))
test_tender_arma_criteria.extend(test_article_16_criteria[:1])


class BaseTenderWebTest(BaseTenderUAWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_arma_data
    initial_config = test_tender_arma_config
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None
    initial_auth = None
    forbidden_question_add_actions_status = (
        "active.pre-qualification"  # status, in which adding tender questions is forbidden
    )
    forbidden_question_update_actions_status = (
        "active.pre-qualification"  # status, in which updating tender questions is forbidden
    )
    question_claim_block_status = "active.pre-qualification"  # status, tender cannot be switched to while it has questions/complaints related to its lot
    # auction role actions
    forbidden_auction_actions_status = "active.pre-qualification.stand-still"  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = (
        "active.pre-qualification.stand-still"  # status, in which adding document to tender auction is forbidden
    )
    periods = PERIODS

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", startend="enquiry_end")

    def set_complaint_period_end(self):
        self.set_status("active.tendering", startend="complaint_end")

    def setUp(self):
        super(BaseTenderUAWebTest, self).setUp()
        self.app.authorization = self.initial_auth or ("Basic", ("token", ""))

    def prepare_award(self):
        # switch to active.pre-qualification
        self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        # qualify bids
        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")
        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
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
                                            "value": (
                                                {
                                                    "yearlyPaymentsPercentage": lot["value"][
                                                        "yearlyPaymentsPercentage"
                                                    ],
                                                    "contractDuration": lot["value"]["contractDuration"],
                                                }
                                                if "contractDuration" in lot["value"]
                                                else lot["value"]
                                            ),
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


class BaseTenderContentWebTest(BaseTenderWebTest):
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super().setUp()
        self.create_tender()
