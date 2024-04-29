import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17, SANDBOX_MODE
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest,
    test_tender_below_bids,
    test_tender_below_data,
    test_tender_below_features_data,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.utils import set_tender_multi_buyers
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.tests.periods import PERIODS

now = get_now()

test_tender_open_data = test_tender_below_data.copy()
test_tender_open_data["procurementMethodType"] = ABOVE_THRESHOLD
del test_tender_open_data["enquiryPeriod"]
test_tender_open_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_tender_open_data["items"] = [
    {
        "description": "футляри до державних нагород",
        "description_en": "Cases for state awards",
        "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
        "additionalClassifications": [
            {"scheme": "ДКПП", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"}
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
]
if SANDBOX_MODE:
    test_tender_open_data["procurementMethodDetails"] = "quick, accelerator=1440"


test_tender_dps_data = deepcopy(test_tender_open_data)
test_tender_dps_data["procurementMethodType"] = "competitiveOrdering"
test_tender_open_bids = deepcopy(test_tender_below_bids)
for bid in test_tender_open_bids:
    bid["selfQualified"] = True
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        bid["selfEligible"] = True

test_tender_open_three_bids = deepcopy(test_tender_open_bids)
test_tender_open_three_bids.append(
    {
        "tenderers": [test_tender_below_organization],
        "value": {"amount": 489.0, "currency": "UAH", "valueAddedTaxIncluded": True},
        "selfQualified": True,
    }
)

test_tender_open_features_data = test_tender_below_features_data.copy()
test_tender_open_features_data["procurementMethodType"] = ABOVE_THRESHOLD
del test_tender_open_features_data["enquiryPeriod"]
test_tender_open_features_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_tender_open_features_data["items"][0]["deliveryDate"] = test_tender_open_data["items"][0]["deliveryDate"]
test_tender_open_features_data["items"][0]["deliveryAddress"] = test_tender_open_data["items"][0]["deliveryAddress"]

test_tender_open_multi_buyers_data = set_tender_multi_buyers(
    test_tender_open_data, test_tender_open_data["items"][0], test_tender_below_organization
)

test_tender_open_config = {
    "hasAuction": True,
    "hasAwardingOrder": True,
    "hasValueRestriction": False,
    "valueCurrencyEquality": True,
    "hasPrequalification": False,
    "minBidsNumber": 1,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": True,
    "hasAwardComplaints": True,
    "hasCancellationComplaints": True,
    "hasQualificationComplaints": False,
    "restricted": False,
}

test_tender_dps_config = {
    "hasAuction": True,
    "hasAwardingOrder": True,
    "hasValueRestriction": False,
    "valueCurrencyEquality": True,
    "hasPrequalification": False,
    "minBidsNumber": 1,
    "hasPreSelectionAgreement": True,
    "hasTenderComplaints": False,
    "hasAwardComplaints": False,
    "hasCancellationComplaints": False,
    "hasQualificationComplaints": False,
    "restricted": False,
}

test_tender_open_complaint_objection = {
    "title": "My objection",
    "description": "Test objection",
    "relatesTo": "tender",
    "relatedItem": "fc390e460c41460b9bde484d6caefc62",
    "classification": {"scheme": "violation_amcu", "id": "corruptionDescription", "description": "test classification"},
    "requestedRemedies": [{"description": "test", "type": "setAsideAward"}],
    "arguments": [{"description": "test argument"}],
    "sequenceNumber": 1,
}


test_agreement_dps_data = {
    "_id": "2e14a78a2074952d5a2d256c3c004dda",
    "doc_type": "Agreement",
    "agreementID": "UA-2021-11-12-000001",
    "agreementType": "dynamicPurchasingSystem",
    "frameworkID": "985a2e3eab47427283a5c51e84d0986d",
    "period": {"startDate": "2021-11-12T00:00:00.318051+02:00", "endDate": "2022-02-24T20:14:24.577158+03:00"},
    "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
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

test_tender_dps_no_auction = deepcopy(test_tender_dps_data)
del test_tender_dps_no_auction["minimalStep"]
test_tender_dps_no_auction["funders"] = [deepcopy(test_tender_below_organization)]
test_tender_dps_no_auction["funders"][0]["identifier"]["id"] = "44000"
test_tender_dps_no_auction["funders"][0]["identifier"]["scheme"] = "XM-DAC"
del test_tender_dps_no_auction["funders"][0]["scale"]


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderUAWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_open_data
    initial_config = test_tender_open_config
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None
    initial_criteria = None
    primary_tender_status = "active.tendering"  # status, to which tender should be switched from 'draft'
    question_claim_block_status = (
        "active.auction"  # status, tender cannot be switched to while it has questions/complaints related to its lot
    )
    forbidden_document_modification_actions_status = (
        "active.auction"  # status, in which operations with tender documents (adding, updating) are forbidden
    )
    forbidden_question_add_actions_status = "active.auction"  # status, in which adding tender questions is forbidden
    forbidden_question_update_actions_status = (
        "active.auction"  # status, in which updating tender questions is forbidden
    )
    forbidden_lot_actions_status = (
        "active.auction"  # status, in which operations with tender lots (adding, updating, deleting) are forbidden
    )
    forbidden_contract_document_modification_actions_status = (
        "unsuccessful"  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    )
    forbidden_auction_actions_status = "active.tendering"  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = (
        "active.tendering"  # status, in which adding document to tender auction is forbidden
    )

    periods = PERIODS

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", startend="enquiry_end")

    def set_complaint_period_end(self):
        self.set_status("active.tendering", startend="complaint_end")

    def set_all_awards_complaint_period_end(self):
        now = get_now()
        startDate = (now - timedelta(days=2)).isoformat()
        endDate = (now - timedelta(days=1)).isoformat()
        tender_document = self.mongodb.tenders.get(self.tender_id)
        for award in tender_document["awards"]:
            award.update({"complaintPeriod": {"startDate": startDate, "endDate": endDate}})
        self.mongodb.tenders.save(tender_document)


class BaseTenderUAContentWebTest(BaseTenderUAWebTest):
    initial_data = test_tender_open_data
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None
    initial_agreement_data = test_agreement_dps_data
    agreement_id = initial_agreement_data["_id"]

    def setUp(self):
        super().setUp()
        if self.initial_data["procurementMethodType"] == "competitiveOrdering":
            self.create_agreement()
            self.initial_data["agreements"] = [{"id": self.agreement_id}]
        self.create_tender()

    def create_agreement(self):
        if self.mongodb.agreements.get(self.agreement_id):
            self.delete_agreement()
        agreement = self.initial_agreement_data
        agreement["dateModified"] = get_now().isoformat()
        self.mongodb.agreements.save(agreement, insert=True)

    def delete_agreement(self):
        self.mongodb.agreements.delete(self.agreement_id)
