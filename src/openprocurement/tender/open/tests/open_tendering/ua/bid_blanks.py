from openprocurement.tender.core.tests.base import test_article_20_criteria
from openprocurement.tender.core.tests.utils import set_bid_responses

SELECTION_CRITERIA_IDS = {criterion["classification"]["id"] for criterion in test_article_20_criteria}

EVIDENCE_DOCUMENT_TYPE_ERROR = [
    {
        "location": "body",
        "name": "requirementResponses",
        "description": [
            {"evidences": [{"relatedDocument": ["relatedDocument should have documentType qualificationDocuments"]}]}
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
    return rrs


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

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"requirementResponses": selection_bid_responses(self, self.doc_id), "status": "pending"}},
        status=422,
    )
    self.assertEqual(response.json["errors"], EVIDENCE_DOCUMENT_TYPE_ERROR)


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

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"requirementResponses": selection_bid_responses(self, doc_id), "status": "pending"}},
        status=422,
    )
    self.assertEqual(response.json["errors"], EVIDENCE_DOCUMENT_TYPE_ERROR)
