import datetime
import os
from copy import deepcopy
from uuid import uuid4

from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import test_docs_lots, test_docs_question, test_docs_tender_dps
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

from openprocurement.api.context import get_now, set_now
from openprocurement.framework.dps.tests.base import (
    test_framework_dps_config,
    test_framework_dps_data,
    test_submission_config,
    test_submission_data,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
)
from openprocurement.tender.competitiveordering.tests.base import (
    BaseTenderUAWebTest,
    test_tender_co_config,
)
from openprocurement.tender.core.tests.base import (
    test_article_16_criteria,
    test_exclusion_criteria,
    test_language_criteria,
)
from openprocurement.tender.core.tests.criteria_utils import generate_responses

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(BASE_DIR, 'source/tendering/competitiveordering/http/')
TARGET_CSV_DIR = os.path.join(BASE_DIR, 'source/tendering/competitiveordering/csv/')


class TenderResourceTest(
    BaseTenderUAWebTest,
    TenderConfigCSVMixin,
    MockWebTestMixin,
):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super().setUp()
        self.setUpMock()
        set_now()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="competitiveOrdering",
            file_path=TARGET_CSV_DIR + "config.csv",
        )

    def create_framework(self):
        data = deepcopy(test_framework_dps_data)
        data["qualificationPeriod"] = {"endDate": (get_now() + datetime.timedelta(days=120)).isoformat()}
        response = self.app.post_json(
            "/frameworks",
            {
                "data": data,
                "config": test_framework_dps_config,
            },
        )
        self.framework_token = response.json["access"]["token"]
        self.framework_id = response.json["data"]["id"]
        return response

    def get_framework(self):
        url = "/frameworks/{}".format(self.framework_id)
        response = self.app.get(url)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        return response

    def activate_framework(self):
        response = self.app.patch_json(
            "/frameworks/{}?acc_token={}".format(self.framework_id, self.framework_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        return response

    def create_submission(self, identifier=uuid4().hex):
        data = deepcopy(test_submission_data)
        data["frameworkID"] = self.framework_id
        data["tenderers"][0]["identifier"]["id"] = identifier
        self.tenderer = data["tenderers"][0]
        response = self.app.post_json(
            "/submissions",
            {
                "data": data,
                "config": test_submission_config,
            },
        )
        self.submission_id = response.json["data"]["id"]
        self.submission_token = response.json["access"]["token"]
        return response

    def activate_submission(self):
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.qualification_id = response.json["data"]["qualificationID"]
        return response

    def activate_qualification(self):
        response = self.app.post_json(
            "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
            {
                "data": {
                    "title": "sign.p7s",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pkcs7-signature",
                    "documentType": "evaluationReports",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        response = self.app.patch_json(
            f"/qualifications/{self.qualification_id}?acc_token={self.framework_token}",
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        return response

    def test_docs_tutorial(self):
        request_path = '/tenders?opt_pretty=1'

        # Create agreement

        self.tick(datetime.timedelta(days=-15))

        self.create_framework()
        self.activate_framework()

        # TODO: fix tick method
        self.tick(datetime.timedelta(days=30))

        self.create_submission(identifier="12345678")
        self.activate_submission()
        self.activate_qualification()

        response = self.get_framework()
        self.agreement_id = response.json["data"]["agreementID"]

        # View agreement

        with open(TARGET_DIR + 'view-agreement-1-contract.http', 'w') as self.app.file_obj:
            response = self.app.get("/agreements/{}".format(self.agreement_id))
            self.assertEqual(response.status, '200 OK')
            agreement = response.json["data"]

        self.app.authorization = ('Basic', ('broker', ''))

        # Creating tender

        data = deepcopy(test_docs_tender_dps)
        data["items"] = [data["items"][0]]
        data["procurementMethodType"] = "competitiveOrdering"
        data['procuringEntity']['identifier']['id'] = test_framework_dps_data['procuringEntity']['identifier']['id']

        data['agreements'] = [{'id': self.agreement_id}]

        lot = deepcopy(test_docs_lots[0])
        lot['value'] = data['value']
        lot['minimalStep'] = data['minimalStep']
        lot['id'] = uuid4().hex

        data['lots'] = [lot]

        config = deepcopy(test_tender_co_config)

        for item in data['items']:
            item['relatedLot'] = lot['id']
            item['deliveryDate'] = {
                "startDate": (get_now() + datetime.timedelta(days=2)).isoformat(),
                "endDate": (get_now() + datetime.timedelta(days=5)).isoformat(),
            }
            item['classification']['id'] = test_framework_dps_data['classification']['id']
        for milestone in data["milestones"]:
            milestone['relatedLot'] = lot['id']

        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # try to add complaint
        with open(TARGET_DIR + 'tender-add-complaint-error.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/complaints?acc_token={owner_token}',
                {'data': test_tender_below_draft_complaint},
                status=403,
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(
                response.json['errors'][0]['description'], "Can't add complaint as it is forbidden by configuration"
            )

        # add relatedLot for item

        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = tender["lots"][0]["id"]
        with open(TARGET_DIR + 'tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": items}}
            )
            self.assertEqual(response.status, '200 OK')

        # add criteria

        test_criteria_data = deepcopy(test_exclusion_criteria)
        for i in range(len(test_criteria_data)):
            classification_id = test_criteria_data[i]['classification']['id']
            if classification_id == 'CRITERION.EXCLUSION.CONTRIBUTIONS.PAYMENT_OF_TAXES':
                del test_criteria_data[i]
                break
        test_criteria_data.extend(test_language_criteria)
        test_criteria_data.extend(test_article_16_criteria[:1])

        with open(TARGET_DIR + 'add-exclusion-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/criteria?acc_token={}'.format(tender_id, owner_token), {'data': test_criteria_data}
            )
            self.assertEqual(response.status, '201 Created')

        # Tender activating (fail)

        with open(TARGET_DIR + 'tender-activating-insufficient-active-contracts-error.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {'data': {"status": "active.tendering"}},
                status=422,
            )
            self.assertEqual(response.status, '422 Unprocessable Entity')
            self.assertEqual(response.json['errors'][0]['description'], "Agreement has less than 3 active contracts")

        # Add agreement contracts

        self.app.authorization = ('Basic', ('broker', ''))

        self.create_submission(identifier="11111111")
        self.activate_submission()
        self.activate_qualification()

        self.create_submission(identifier="22222222")
        self.activate_submission()
        self.activate_qualification()

        # Tender activating
        with open(TARGET_DIR + 'notice-document-required.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {'data': {"status": "active.tendering"}},
                status=422,
            )

        with open(TARGET_DIR + 'add-notice-document.http', 'w') as self.app.file_obj:
            self.add_sign_doc(tender_id, owner_token)

        with open(TARGET_DIR + 'tender-activating.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.tendering"}}
            )
            self.assertEqual(response.status, '200 OK')

        # asking questions
        docs_data = deepcopy(test_docs_question)
        docs_data["author"]["identifier"]["id"] = "11112222"
        with open(TARGET_DIR + 'ask-question-invalid-author.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id), {'data': docs_data}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')

        docs_data["author"]["identifier"]["id"] = agreement["contracts"][0]["suppliers"][0]["identifier"]["id"]
        with open(TARGET_DIR + 'ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id), {'data': docs_data}, status=201
            )
            question_id = response.json["data"]["id"]
            self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question_id, owner_token),
            {"data": {"answer": "answer"}},
        )
        self.assertEqual(response.status, "200 OK")

        # Setting Bid guarantee

        response = self.app.patch_json(
            f'/tenders/{self.tender_id}?acc_token={owner_token}',
            {'data': {"guarantee": {"amount": 8, "currency": "USD"}}},
        )
        self.assertEqual(response.status, '200 OK')
        self.assertIn('guarantee', response.json['data'])

        # Uploading documentation
        response = self.app.post_json(
            f'/tenders/{self.tender_id}/documents?acc_token={owner_token}',
            {
                "data": {
                    "title": "Notice.pdf",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                }
            },
        )
        self.assertEqual(response.status, '201 Created')

        # Registering bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json(
            f'/tenders/{tender_id}/bids',
            {
                'data': {
                    'selfQualified': True,
                    'status': 'draft',
                    'tenderers': [self.tenderer],
                    'lotValues': [
                        {
                            "subcontractingDetails": "ДКП «Орфей», Україна",
                            "value": {"amount": 500},
                            'relatedLot': lot['id'],
                        }
                    ],
                }
            },
        )
        self.assertEqual(response.status, '201 Created')
        bid1_token = response.json['access']['token']
        bid1_id = response.json['data']['id']

        requirement_responses = generate_responses(self)
        response = self.app.patch_json(
            f'/tenders/{self.tender_id}/bids/{bid1_id}?acc_token={bid1_token}',
            {'data': {"requirementResponses": requirement_responses}},
        )
        self.assertEqual(response.status, '200 OK')
        self.add_sign_doc(
            self.tender_id,
            bid1_token,
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
        )

        response = self.app.patch_json(
            f'/tenders/{self.tender_id}/bids/{bid1_id}?acc_token={bid1_token}', {'data': {"status": "pending"}}
        )
        self.assertEqual(response.status, '200 OK')

        # Registering bid 2
        response = self.app.post_json(
            f'/tenders/{tender_id}/bids',
            {
                'data': {
                    'selfQualified': True,
                    'status': 'draft',
                    'tenderers': [self.tenderer],
                    'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot["id"]}],
                }
            },
        )
        self.assertEqual(response.status, '201 Created')
        bid2_id = response.json['data']['id']
        bid2_token = response.json['access']['token']
        self.add_sign_doc(
            self.tender_id,
            bid2_token,
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json, "pending")

        lot_values = response.json["data"]["lotValues"]

        # Bids confirmation
        response = self.app.patch_json(
            f'/tenders/{tender_id}/bids/{bid2_id}?acc_token={bid2_token}',
            {
                'data': {
                    'lotValues': [{**lot_values[0], "value": {"amount": 500}, 'relatedLot': lot["id"]}],
                    'status': 'pending',
                }
            },
        )
        self.assertEqual(response.status, '200 OK')

        # Registering bid 3
        agreement = self.mongodb.agreements.get(self.agreement_id)
        tenderer = deepcopy(self.tenderer)
        tenderer["identifier"]["id"] = agreement["contracts"][1]["suppliers"][0]["identifier"]["id"]
        with open(TARGET_DIR + 'register-third-bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'selfQualified': True,
                        'status': 'draft',
                        'tenderers': [tenderer],
                        'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot["id"]}],
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')
        bid3_id = response.json['data']['id']
        bid3_token = response.json['access']['token']
        self.add_sign_doc(
            self.tender_id,
            bid3_token,
            docs_url=f"/bids/{bid3_id}/documents",
            document_type="proposal",
        )
        self.set_responses(tender_id, response.json, "pending")

        # disqualify second supplier from agreement during active.tendering
        agreement["contracts"][1]["status"] = "terminated"
        self.mongodb.agreements.save(agreement)

        self.set_status("active.tendering", startend="end")
        self.check_chronograph()
        with open(TARGET_DIR + 'active-tendering-end-not-member-bid.http', 'w') as self.app.file_obj:
            response = self.app.get(
                f'/tenders/{tender_id}/bids/{bid3_id}?acc_token={bid3_token}',
            )
            self.assertEqual(response.status, '200 OK')

        #  Auction
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        auction1_url = f'{self.auctions_url}/tenders/{self.tender_id}_{lot["id"]}'
        patch_data = {
            'lots': [
                {
                    'id': lot["id"],
                    'auctionUrl': auction1_url,
                }
            ],
            'bids': [
                {
                    "id": bid1_id,
                    "lotValues": [
                        {"participationUrl": f'{auction1_url}?key_for_bid={bid1_id}'},
                    ],
                },
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": f'{auction1_url}?key_for_bid={bid2_id}'},
                    ],
                },
                {
                    "id": bid3_id,
                    "lotValues": [
                        {"participationUrl": f'{auction1_url}?key_for_bid={bid3_id}'},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            f'/tenders/{self.tender_id}/auction/{lot["id"]}?acc_token={owner_token}', {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')

        # Confirming qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get(f'/tenders/{self.tender_id}/auction')
        auction_bids_data = response.json['data']['bids']
        auction_bids_data[0]["lotValues"][0]["value"]["amount"] = 250  # too low price

        self.app.post_json(
            f'/tenders/{self.tender_id}/auction/{lot["id"]}',
            {
                'data': {
                    'bids': [
                        {
                            "id": bid["id"],
                            "lotValues": [
                                {"value": lot_value["value"], "relatedLot": lot_value["relatedLot"]}
                                for lot_value in bid["lotValues"]
                            ],
                        }
                        for bid in auction_bids_data
                    ]
                }
            },
        )

        self.app.authorization = ('Basic', ('broker', ''))

        # get pending award
        response = self.app.get(f'/tenders/{self.tender_id}/awards?acc_token={owner_token}')

        award = response.json["data"][0]
        award_id = award["id"]
        self.assertEqual(len(award.get("milestones", "")), 1)
        tender = self.mongodb.tenders.get(self.tender_id)
        tender["awards"][0]["milestones"][0]["dueDate"] = (get_now() - datetime.timedelta(days=1)).isoformat()
        self.mongodb.tenders.save(tender)

        self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
        self.app.patch_json(
            f'/tenders/{self.tender_id}/awards/{award_id}?acc_token={owner_token}',
            {"data": {"status": "active", "qualified": True}},
            status=200,
        )

        with open(TARGET_DIR + 'tender-get-award.http', 'w') as self.app.file_obj:
            self.app.get(f'/tenders/{self.tender_id}/awards/{award_id}')

        # try to add complaint to award
        with open(TARGET_DIR + 'tender-add-complaint-qualification-error.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/awards/{award_id}/complaints?acc_token={bid2_token}',
                {'data': test_tender_below_draft_complaint},
                status=403,
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(
                response.json['errors'][0]['description'], "Can't add complaint as it is forbidden by configuration"
            )

        # Preparing the cancellation request

        response = self.app.post_json(
            f'/tenders/{self.tender_id}/cancellations?acc_token={owner_token}',
            {'data': {'reason': 'cancellation reason', 'reasonType': 'unFixable'}},
        )
        self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        #  Filling cancellation with protocol and supplementary documentation

        response = self.app.post_json(
            f'/tenders/{self.tender_id}/cancellations/{cancellation_id}/documents?acc_token={owner_token}',
            {
                "data": {
                    "title": "Notice.pdf",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                }
            },
        )
        self.assertEqual(response.status, '201 Created')

        # try to add complaint to cancellation
        with open(TARGET_DIR + 'tender-add-complaint-cancellation-error.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/cancellations/{cancellation_id}/complaints?acc_token={owner_token}',
                {'data': test_tender_below_draft_complaint},
                status=403,
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(
                response.json['errors'][0]['description'], "Can't add complaint as it is forbidden by configuration"
            )

        # Activating the request and cancelling tender
        with open(TARGET_DIR + 'pending-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{self.tender_id}/cancellations/{cancellation_id}?acc_token={owner_token}',
                {'data': {"status": "pending"}},
            )
            self.assertEqual(response.status, '200 OK')

        response = self.app.get(f'/tenders/{self.tender_id}?acc_token={owner_token}')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json["data"]["status"], "cancelled")
