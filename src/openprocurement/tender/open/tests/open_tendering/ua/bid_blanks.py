from copy import deepcopy

from openprocurement.tender.core.constants import CRITERION_SUBCONTRACTING_PROPORTION
from openprocurement.tender.core.tests.base import test_article_20_criteria
from openprocurement.tender.core.tests.utils import (
    set_bid_items,
    set_bid_lotvalues,
    set_bid_responses,
)
from openprocurement.tender.open.tests.open_tendering.ua.base import (
    test_tender_open_tendering_ua_bids,
)

SELECTION_CRITERIA_IDS = {criterion["classification"]["id"] for criterion in test_article_20_criteria}


def evidence_document_type_error(requirement_id):
    return [
        {
            "location": "body",
            "name": "requirementResponses",
            "description": [
                {
                    "evidences": [
                        {
                            "relatedDocument": [
                                "relatedDocument should have documentType qualificationDocuments "
                                f"(requirement {requirement_id})"
                            ]
                        }
                    ]
                }
            ],
        }
    ]


def selection_bid_responses(self, doc_id):
    """
    Bid requirement responses with a document evidence of a selection (article 20) criterion
    """
    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    criteria = [criterion for criterion in response.json["data"] if criterion["source"] in ("tenderer", "winner")]
    selection_requirement_ids = {
        requirement["id"]
        for criterion in criteria
        if criterion["classification"]["id"] in SELECTION_CRITERIA_IDS
        for group in criterion["requirementGroups"]
        for requirement in group["requirements"]
    }
    rrs = set_bid_responses(criteria)
    selection_rr = next(rr for rr in rrs if rr["requirement"]["id"] in selection_requirement_ids)
    selection_rr["evidences"] = [
        {
            "title": "Requirement response",
            "type": "document",
            "relatedDocument": {"id": doc_id, "title": "name.doc"},
        }
    ]
    return rrs, selection_rr["requirement"]["id"]


def bid_evidence_document_version(self):
    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.bid_id, self.doc_id, self.bid_token
        ),
        {
            "data": {
                "title": "name2.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.bid_id, self.doc_id, self.bid_token
        ),
        {"data": {"documentType": "eligibilityDocuments"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"].get("documentType"), "eligibilityDocuments")

    bid = self.mongodb.tenders.get(self.tender_id)["bids"][0]
    versions = [document for document in bid["documents"] if document["id"] == self.doc_id]
    self.assertEqual(
        [document.get("documentType") for document in versions],
        ["qualificationDocuments", "eligibilityDocuments"],
    )

    rrs, requirement_id = selection_bid_responses(self, self.doc_id)
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"requirementResponses": rrs, "status": "pending"}},
        status=422,
    )
    self.assertEqual(response.json["errors"], evidence_document_type_error(requirement_id))


def bid_activate_with_invalid_evidence_document_type(self):
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentType": "proposal",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    doc_id = response.json["data"]["id"]

    rrs, requirement_id = selection_bid_responses(self, doc_id)
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"requirementResponses": rrs, "status": "pending"}},
        status=422,
    )
    self.assertEqual(response.json["errors"], evidence_document_type_error(requirement_id))


def bid_responses_with_evidence(self, classification_id, doc_id):
    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    criteria = [criterion for criterion in response.json["data"] if criterion["source"] in ("tenderer", "winner")]
    requirement_ids = {
        requirement["id"]
        for criterion in criteria
        if criterion["classification"]["id"] == classification_id
        for group in criterion["requirementGroups"]
        for requirement in group["requirements"]
    }
    rrs = set_bid_responses(criteria)
    requirement_response = next(rr for rr in rrs if rr["requirement"]["id"] in requirement_ids)
    requirement_response["evidences"] = [
        {
            "title": "Requirement response",
            "type": "document",
            "relatedDocument": {"id": doc_id, "title": "name.doc"},
        }
    ]
    return rrs, requirement_response["requirement"]["id"]


def create_bid_document(self, bid_id, bid_token, container, document_type):
    response = self.app.post_json(
        "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, bid_id, container, bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentType": document_type,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    return response.json["data"]["id"]


def bid_evidence_document_type(self):
    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    selection_classification_id = next(
        criterion["classification"]["id"]
        for criterion in response.json["data"]
        if criterion["classification"]["id"] in SELECTION_CRITERIA_IDS
    )
    cases = (
        ("CRITERION.EXCLUSION.CONVICTIONS.FRAUD", "eligibility_documents", "eligibilityDocuments", "documents"),
        (selection_classification_id, "documents", "qualificationDocuments", "eligibility_documents"),
    )
    for classification_id, container, document_type, other_container in cases:
        bid_data = deepcopy(getattr(self, "test_bids_data", test_tender_open_tendering_ua_bids)[0])
        if self.initial_lots:
            set_bid_lotvalues(bid_data, self.initial_lots)
        set_bid_items(self, bid_data)
        bid_data["status"] = "draft"
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
        bid_id = response.json["data"]["id"]
        bid_token = response.json["access"]["token"]
        self.add_sign_doc(self.tender_id, bid_token, docs_url=f"/bids/{bid_id}/documents", document_type="proposal")
        bid_path = "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token)

        other_container_doc_id = create_bid_document(self, bid_id, bid_token, other_container, document_type)
        rrs, requirement_id = bid_responses_with_evidence(self, classification_id, other_container_doc_id)
        response = self.app.patch_json(
            bid_path,
            {"data": {"requirementResponses": rrs, "status": "pending"}},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "requirementResponses",
                    "description": [
                        {
                            "evidences": [
                                {
                                    "relatedDocument": [
                                        "relatedDocument.id should be one of bid documents "
                                        f"(requirement {requirement_id})"
                                    ]
                                }
                            ]
                        }
                    ],
                }
            ],
        )

        wrong_type_doc_id = create_bid_document(self, bid_id, bid_token, container, "biddingDocuments")
        rrs, requirement_id = bid_responses_with_evidence(self, classification_id, wrong_type_doc_id)
        response = self.app.patch_json(
            bid_path,
            {"data": {"requirementResponses": rrs, "status": "pending"}},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "requirementResponses",
                    "description": [
                        {
                            "evidences": [
                                {
                                    "relatedDocument": [
                                        f"relatedDocument should have documentType {document_type} "
                                        f"(requirement {requirement_id})"
                                    ]
                                }
                            ]
                        }
                    ],
                }
            ],
        )

        doc_id = create_bid_document(self, bid_id, bid_token, container, document_type)
        rrs, requirement_id = bid_responses_with_evidence(self, classification_id, doc_id)
        response = self.app.patch_json(
            bid_path,
            {"data": {"requirementResponses": rrs, "status": "pending"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")


def winner_evidence_document_type(self):
    bid_id = self.initial_bids[0]["id"]
    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    requirement_ids = {
        requirement["id"]
        for criterion in response.json["data"]
        if criterion["classification"]["id"] == CRITERION_SUBCONTRACTING_PROPORTION
        for group in criterion["requirementGroups"]
        for requirement in group["requirements"]
    }
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, self.bid_token))
    requirement_response = next(
        rr for rr in response.json["data"]["requirementResponses"] if rr["requirement"]["id"] in requirement_ids
    )

    evidences_path = "/tenders/{}/bids/{}/requirement_responses/{}/evidences?acc_token={}".format(
        self.tender_id, bid_id, requirement_response["id"], self.bid_token
    )

    def post_evidence(doc_id, status=201):
        return self.app.post_json(
            evidences_path,
            {
                "data": {
                    "title": "Requirement response",
                    "type": "document",
                    "relatedDocument": {"id": doc_id},
                }
            },
            status=status,
        )

    other_container_doc_id = create_bid_document(self, bid_id, self.bid_token, "documents", "qualificationDocuments")
    response = post_evidence(other_container_doc_id, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "relatedDocument",
                "description": [
                    "relatedDocument.id should be one of bid documents "
                    f"(requirement {requirement_response['requirement']['id']})"
                ],
            }
        ],
    )

    wrong_type_doc_id = create_bid_document(
        self, bid_id, self.bid_token, "qualification_documents", "eligibilityDocuments"
    )
    response = post_evidence(wrong_type_doc_id, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "relatedDocument",
                "description": [
                    "relatedDocument should have documentType qualificationDocuments "
                    f"(requirement {requirement_response['requirement']['id']})"
                ],
            }
        ],
    )

    doc_id = create_bid_document(self, bid_id, self.bid_token, "qualification_documents", "qualificationDocuments")
    response = post_evidence(doc_id)
    self.assertEqual(response.json["data"]["relatedDocument"]["id"], doc_id)
