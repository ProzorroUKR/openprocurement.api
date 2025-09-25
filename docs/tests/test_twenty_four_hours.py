import os
from copy import deepcopy
from datetime import timedelta

from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import (
    test_docs_bid2,
    test_docs_bid_draft,
    test_docs_qualified,
    test_docs_subcontracting,
    test_docs_tender_openua,
)
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.core.tests.criteria_utils import generate_responses
from openprocurement.tender.core.tests.utils import (
    set_bid_lotvalues,
    set_tender_criteria,
)
from openprocurement.tender.openua.tests.base import test_tender_openua_criteria
from openprocurement.tender.openua.tests.tender import BaseTenderUAWebTest

TARGET_DIR = 'docs/source/tendering/basic-actions/http/'

test_tender_ua_data = deepcopy(test_docs_tender_openua)
bid = deepcopy(test_docs_bid_draft)
bid2 = deepcopy(test_docs_bid2)

bid2.update(test_docs_qualified)
bid.update(test_docs_subcontracting)
bid.update(test_docs_qualified)


class TenderAwardMilestoneResourceTest(BaseTenderUAWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_ua_data
    initial_lots = test_tender_below_lots
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_milestone(self):
        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json(
            '/tenders?opt_pretty=1', {'data': test_tender_ua_data, 'config': self.initial_config}
        )
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender["id"]

        # add lots
        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(self.tender_id, owner_token), {'data': self.initial_lots[0]}
        )
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token), {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        # Tender activating
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        tender = response.json["data"]

        test_criteria_data = deepcopy(test_tender_openua_criteria)
        set_tender_criteria(test_criteria_data, tender["lots"], tender["items"])

        response = self.app.post_json(
            '/tenders/{}/criteria?acc_token={}'.format(tender['id'], owner_token), {'data': test_criteria_data}
        )
        self.assertEqual(response.status, '201 Created')

        self.add_sign_doc(tender['id'], owner_token)

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {"status": "active.tendering"}}
        )
        self.assertEqual(response.status, '200 OK')

        # Registering bid

        bids_access = {}
        bid_data = deepcopy(bid)
        set_bid_lotvalues(bid_data, self.initial_lots)
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid_data})
        bid1_id = response.json['data']['id']
        bids_access[bid1_id] = response.json['access']['token']
        self.assertEqual(response.status, '201 Created')

        requirementResponses = generate_responses(self)
        response = self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
            {'data': {"requirementResponses": requirementResponses}},
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
            {
                'data': {
                    'title': 'Proposal.p7s',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'sign/p7s',
                    'documentType': 'proposal',
                }
            },
        )
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
            {'data': {"status": "pending"}},
        )
        self.assertEqual(response.status, '200 OK')
        bid1 = response.json["data"]

        bid2_data = deepcopy(bid2)
        bid2_data["status"] = "draft"
        set_bid_lotvalues(bid2_data, self.initial_lots)
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid2_data})
        bid2_id = response.json['data']['id']
        bids_access[bid2_id] = response.json['access']['token']
        self.assertEqual(response.status, '201 Created')

        self.add_sign_doc(
            self.tender_id,
            bids_access[bid2_id],
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json)

        # Auction
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        auction_url = '{}/tenders/{}_{}'.format(self.auctions_url, self.tender_id, lot_id)
        patch_data = {
            'lots': [
                {
                    'id': lot_id,
                    'auctionUrl': auction_url,
                },
            ],
            'bids': [
                {"id": bid1_id, "lotValues": [{"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid1_id)}]},
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid2_id)},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id, owner_token), {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')

        # Confirming qualification
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        auction_bids_data[0]["lotValues"][0]["value"]["amount"] = 250  # too low price

        self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot_id),
            {
                'data': {
                    'bids': [
                        {
                            "id": b["id"],
                            "lotValues": [
                                {"value": lot["value"], "relatedLot": lot["relatedLot"]} for lot in b["lotValues"]
                            ],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
        )
        self.app.authorization = ('Basic', ('broker', ''))

        # get pending award
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))

        award = response.json["data"][0]
        self.award_id = award["id"]
        self.assertEqual(len(award.get("milestones", "")), 1)

        # valid creation
        request_data = {"code": "24h", "description": "One ring to bring them all and in the darkness bind them"}
        with open(TARGET_DIR + '24hours/award-milestone-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/awards/{}/milestones?acc_token={}".format(self.tender_id, self.award_id, owner_token),
                {"data": request_data},
            )
        self.assertEqual(response.status, "201 Created")

        self.tick()

        with open(TARGET_DIR + '24hours/award-patch.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
                status=403,
            )

        # try upload documents
        bid_id = bid1_id
        bid_token = bids_access[bid1_id]

        with open(TARGET_DIR + '24hours/post-doc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
                {
                    "data": {
                        "title": "укр.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
                status=201,
            )
            doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + '24hours/put-doc.http', 'w') as self.app.file_obj:
            self.app.put_json(
                "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                    self.tender_id, bid_id, response.json["data"]["id"], bid_token
                ),
                {
                    "data": {
                        "title": "укр.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
                status=200,
            )

        bid1["tenderers"][0]["signerInfo"]["name"] = "Бойко Микола Миколайович>"
        bid1["tenderers"][0]["signerInfo"]["iban"] = "111111111222222"
        with open(TARGET_DIR + '24hours/patch-bid.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
                {
                    "data": {
                        "subcontractingDetails": "ДП «Орфей»",
                        "tenderers": bid1["tenderers"],
                    }
                },
                status=200,
            )

        bid1["tenderers"][0]["address"]["streetAddress"] = "вул. Островського, 3"

        with open(TARGET_DIR + '24hours/patch-bid-invalid.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
                {
                    "data": {
                        "tenderers": bid1["tenderers"],
                    }
                },
                status=422,
            )

        article_17_req_response_id = ""
        for req_resp in bid1["requirementResponses"]:
            if (
                req_resp["classification"]["id"]
                == "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION"
            ):
                article_17_req_response_id = req_resp["id"]

        with open(TARGET_DIR + '24hours/delete-article-17-req-response.http', 'w') as self.app.file_obj:
            self.app.delete(
                "/tenders/{}/bids/{}/requirement_responses/{}?acc_token={}".format(
                    self.tender_id, bid_id, article_17_req_response_id, bid_token
                ),
            )

        response = self.app.get(f"/tenders/{self.tender_id}/criteria")
        article_17_req_id = ""
        for criterion in response.json["data"]:
            if (
                criterion["classification"]["id"]
                == "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION"
            ):
                article_17_req_id = criterion["requirementGroups"][-1]["requirements"][0]["id"]  # take second req group
                break

        with open(TARGET_DIR + '24hours/add-article-17-req-response.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, bid_id, bid_token),
                {
                    "data": {
                        "requirement": {
                            "id": article_17_req_id,
                        },
                        "value": True,
                    }
                },
            )
            req_resp_id = response.json["data"][0]["id"]

        evidence_data = {
            "title": "Requirement response",
            "relatedDocument": {
                "id": doc_id,
                "title": "name.doc",
            },
            "type": "document",
        }

        with open(TARGET_DIR + '24hours/add-req-responses-evidences.http', 'w') as self.app.file_obj:
            self.app.post_json(
                "/tenders/{}/bids/{}/requirement_responses/{}/evidences?acc_token={}".format(
                    self.tender_id, bid_id, req_resp_id, bid_token
                ),
                {"data": evidence_data},
            )

        self.tick(delta=timedelta(days=1))  # after milestone.dueDate passed

        with open(TARGET_DIR + '24hours/patch-bid-forbidden.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
                {
                    "data": {
                        "subcontractingDetails": "ДП «Орфей», Україна",
                    }
                },
                status=403,
            )

        # qualification milestone creation
        tender = self.mongodb.tenders.get(self.tender_id)
        tender["procurementMethodType"] = "aboveThresholdEU"
        tender["title_en"] = " "
        tender["procuringEntity"]["name_en"] = " "
        tender["procuringEntity"]["identifier"]["legalName_en"] = " "
        tender["procuringEntity"]["contactPoint"]["name_en"] = " "
        tender["status"] = "active.pre-qualification"
        tender_end = get_now() + timedelta(days=30, seconds=10)
        tender["tenderPeriod"]["endDate"] = tender_end.isoformat()
        tender["awardPeriod"]["startDate"] = tender_end.isoformat()
        qualification_id = "1234" * 8
        tender["qualifications"] = [
            {
                "id": qualification_id,
                "bidID": bid_id,
                "status": "pending",
            }
        ]
        del tender["awards"]
        self.mongodb.tenders.save(tender)

        self.tick()

        with open(TARGET_DIR + '24hours/qualification-milestone-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/qualifications/{}/milestones?acc_token={}".format(
                    self.tender_id, qualification_id, owner_token
                ),
                {"data": request_data},
            )
        self.assertEqual(response.status, "201 Created")
