# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from mock import patch
from datetime import timedelta

from openprocurement.api.models import get_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.open.tests.tender import BaseTenderUAWebTest
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_language_criteria,
)
from openprocurement.tender.core.tests.criteria_utils import generate_responses
from tests.base.constants import (
    DOCS_URL,
    AUCTIONS_URL,
)
from tests.base.test import (
    DumpsWebTestApp,
    MockWebTestMixin,
)
from tests.base.data import (
    test_docs_question,
    test_docs_tender_open,
    test_docs_bid_draft,
    test_docs_bid2,
    test_docs_subcontracting,
    test_docs_qualified,
    test_docs_lots,
)

test_tender_data = deepcopy(test_docs_tender_open)
test_lots = deepcopy(test_docs_lots)
bid = deepcopy(test_docs_bid_draft)
bid2 = deepcopy(test_docs_bid2)

bid2.update(test_docs_qualified)
bid.update(test_docs_subcontracting)
bid.update(test_docs_qualified)

test_lots[0]['value'] = test_tender_data['value']
test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
test_lots[1]['value'] = test_tender_data['value']
test_lots[1]['minimalStep'] = test_tender_data['minimalStep']

TARGET_DIR = 'docs/source/tendering/open/http/'


class TenderResourceTest(BaseTenderUAWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super(TenderResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderResourceTest, self).tearDown()

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules

        with open(TARGET_DIR + 'tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        with open(TARGET_DIR + 'tender-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=422)

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tender-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post(
                request_path, 'data', content_type='application/json', status=422
            )
            self.assertEqual(response.status, '422 Unprocessable Entity')

        #### Creating tender

        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # add lots
        with open(TARGET_DIR + 'tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': test_lots[0]}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
            {'data': test_lots[1]}
        )
        self.assertEqual(response.status, '201 Created')
        lot2 = response.json['data']
        lot_id2 = lot2['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        items[1]["relatedLot"] = lot_id2
        with open(TARGET_DIR + 'tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {"data": {"items": items}}
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

        with open(TARGET_DIR + 'add-exclusion-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/criteria?acc_token={}'.format(tender_id, owner_token),
                {'data': test_criteria_data}
            )
            self.assertEqual(response.status, '201 Created')

        #### Tender activating
        with open(TARGET_DIR + 'tender-activating.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {'data': {"status": "active.tendering"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'active-tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        #### Modifying tender

        self.app.authorization = ('Basic', ('broker', ''))
        tender_period_end_date = get_now() + timedelta(days=16)
        with open(TARGET_DIR + 'patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {
                    'data': {
                        "tenderPeriod": {
                            "startDate": tender["tenderPeriod"]["startDate"],
                            "endDate": tender_period_end_date.isoformat(),
                        }
                    }
                }
            )

        with open(TARGET_DIR + 'tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        # Setting Bid guarantee

        with open(TARGET_DIR + 'set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(
                    self.tender_id, owner_token
                ),
                {'data': {"guarantee": {"amount": 8, "currency": "USD"}}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        #### Uploading documentation

        with open(TARGET_DIR + 'upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(
                    self.tender_id, owner_token
                ),
                {
                    "data": {
                        "title": "Notice.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf"
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + 'tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token
                )
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(
                    self.tender_id, owner_token
                ),
                {
                    "data": {
                        "title": "AwardCriteria.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf"
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/documents?acc_token={}'.format(
                    self.tender_id, owner_token
                )
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token
                ),
                {
                    "data": {
                        "title": "AwardCriteria-2.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf"
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/documents'.format(self.tender_id)
            )
            self.assertEqual(response.status, '200 OK')

        #### Enquiries

        with open(TARGET_DIR + 'ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': test_docs_question}, status=201
            )
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/questions/{}?acc_token={}'.format(
                    self.tender_id, question_id, owner_token
                ),
                {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}}, status=200
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'list-question.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/questions'.format(
                    self.tender_id
                )
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/questions/{}'.format(
                    self.tender_id, question_id
                )
            )
            self.assertEqual(response.status, '200 OK')

        self.set_enquiry_period_end()
        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"value": {'amount': 501.0}}}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': test_docs_question}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')

        response = self.app.get(f"/tenders/{self.tender_id}")
        tender = response.json["data"]
        with open(TARGET_DIR + 'update-tender-after-enqiery-with-update-periods.http', 'w') as self.app.file_obj:
            tender_period_end_date = get_now() + timedelta(days=8)
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {
                    'data': {
                        "value": {
                            "amount": 501,
                            "currency": "UAH"
                        },
                        "tenderPeriod": {
                            "startDate": tender["tenderPeriod"]["startDate"],
                            "endDate": tender_period_end_date.isoformat(),
                        }
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        #### Registering bid
        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'bid-lot1.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'selfQualified': True,
                        'status': 'draft',
                        'tenderers': bid["tenderers"],
                        'lotValues': [{
                            "subcontractingDetails": "ДКП «Орфей», Україна",
                            "value": {"amount": 500},
                            'relatedLot': lot_id1
                        }]
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')
            bid1_token = response.json['access']['token']
            bid1_id = response.json['data']['id']

        requirementResponses = generate_responses(self)
        with open(TARGET_DIR + 'add-requirement-responses-to-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bid1_token
                ),
                {'data': {"requirementResponses": requirementResponses}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bid1_token
                ),
                {'data': {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')

        #### Proposal Uploading

        with open(TARGET_DIR + 'upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bid1_token
                ),
                {
                    "data": {
                        "title": "Proposal.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf"
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bid1_token
                )
            )
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
            {'data': {"value": {'amount': 501.0}}}
        )
        self.assertEqual(response.status, '200 OK')

        #### Registering bid 2
        with open(TARGET_DIR + 'bid-lot2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'selfQualified': True,
                        'status': 'draft',
                        'tenderers': test_docs_bid2["tenderers"],
                        'lotValues': [{
                            "value": {"amount": 500},
                            'relatedLot': lot_id1
                        }, {
                            "subcontractingDetails": "ДКП «Укр Прінт», Україна",
                            "value": {"amount": 500},
                            'relatedLot': lot_id2
                        }]
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')
            bid2_id = response.json['data']['id']
            bid2_token = response.json['access']['token']
        self.set_responses(tender_id, response.json, "active")

        #### Bids invalidation
        with open(TARGET_DIR + 'tender-invalid-all-bids.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{tender_id}/lots/{lot_id2}?acc_token={owner_token}',
                {'data': {'value': {**lot2['value'], 'amount': 400}}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bid-lot1-invalid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid1_id, bid1_token))
            self.assertEqual(response.status, '200 OK')

        #### Bids confirmation
        with open(TARGET_DIR + 'bid-lot1-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid1_id, bid1_token),
                {
                    'data': {
                        'lotValues': [{
                            "subcontractingDetails": "ДКП «Орфей»",
                            "value": {"amount": 500},
                            'relatedLot': lot_id1
                        }],
                        'status': 'active'
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bid-lot2-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{tender_id}/bids/{bid2_id}?acc_token={bid2_token}',
                {
                    'data': {
                        'lotValues': [{
                            "value": {"amount": 500},
                            'relatedLot': lot_id1
                        }, {
                            'relatedLot': lot_id2,
                        }],
                        'status': 'active'
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        #### Auction
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        auction1_url = '{}/tenders/{}_{}'.format(self.auctions_url, self.tender_id, lot_id1)
        auction2_url = '{}/tenders/{}_{}'.format(self.auctions_url, self.tender_id, lot_id2)
        patch_data = {
            'lots': [
                {
                    'id': lot_id1,
                    'auctionUrl': auction1_url,
                },
                {
                    'id': lot_id2,
                },
            ],
            'bids': [{
                "id": bid1_id,
                "lotValues": [
                    {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid1_id)}
                ]
            }, {
                "id": bid2_id,
                "lotValues": [
                    {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid2_id)},
                ]
            }]
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id1, owner_token),
            {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bid1_token)
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bid2_token)
            )
            self.assertEqual(response.status, '200 OK')

        #### Confirming qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        auction_bids_data[0]["lotValues"][0]["value"]["amount"] = 250  # too low price

        response = self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot_id1),
            {
                'data': {
                    'bids': [
                        {
                            "id": b["id"], "lotValues": [
                            {"value": l["value"], "relatedLot": l["relatedLot"]}
                            for l in b["lotValues"]
                        ]
                        }
                        for b in auction_bids_data
                    ]
                }
            }
        )

        self.app.authorization = ('Basic', ('broker', ''))

        # get pending award
        with open(TARGET_DIR + 'get-awards-list.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))

        award = response.json["data"][0]
        award_id = award["id"]
        award_bid_id = award["bid_id"]
        self.assertEqual(len(award.get("milestones", "")), 1)

        with open(TARGET_DIR + 'fail-disqualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {
                    "data": {
                        "status": "unsuccessful",
                    }
                },
                status=403
            )

        with open(TARGET_DIR + 'post-evidence-document.http', 'w') as self.app.file_obj:
            self.app.post_json(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(
                    self.tender_id, award_bid_id, bid1_token
                ),
                {
                    "data": {
                        "title": "lorem.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                        "documentType": "evidence"
                    }
                },
                status=201
            )

        tender = self.mongodb.tenders.get(self.tender_id)
        tender["awards"][0]["milestones"][0]["dueDate"] = (get_now() - timedelta(days=1)).isoformat()
        self.mongodb.tenders.save(tender)

        with open(TARGET_DIR + 'confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {
                    "data": {
                        "status": "active",
                        "qualified": True,
                        "eligible": True
                    }
                },
                status=200
            )

        response = self.app.get(
            '/tenders/{}/contracts?acc_token={}'.format(
                self.tender_id, owner_token
            )
        )
        self.contract_id = response.json['data'][0]['id']

        ####  Set contract value

        tender = self.mongodb.tenders.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.mongodb.tenders.save(tender)

        with open(TARGET_DIR + 'tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {"data": {"value": {"amount": 238, "amountNet": 230}}}
            )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        #### Setting contract signature date

        self.tick()

        with open(TARGET_DIR + 'tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {'data': {"dateSigned": get_now().isoformat()}}
            )
            self.assertEqual(response.status, '200 OK')

        #### Setting contract period

        period_dates = {
            "period": {
                "startDate": (get_now()).isoformat(),
                "endDate": (get_now() + timedelta(days=365)).isoformat()
            }
        }
        with open(TARGET_DIR + 'tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {'data': {'period': period_dates["period"]}}
            )
        self.assertEqual(response.status, '200 OK')

        #### Uploading contract documentation

        with open(TARGET_DIR + 'tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {
                    "data": {
                        "title": "contract_document.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf"
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')
            self.document_id = response.json['data']['id']

        with open(TARGET_DIR + 'tender-contract-get.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                )
            )
            self.assertEqual(response.status, '200 OK')

        #### Preparing the cancellation request

        with open(TARGET_DIR + 'prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token
                ),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'unFixable'}}
            )
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token
                ),
                {'data': {'reasonType': 'forceMajeure'}}
            )
            self.assertEqual(response.status, '200 OK')

        #### Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token
                ),
                {
                    "data": {
                        "title": "Notice.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf"
                    }
                }
            )
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {'data': {"description": 'Changed description'}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {
                    "data": {
                        "title": "Notice-2.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf"
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        #### Activating the request and cancelling tender
        with open(TARGET_DIR + 'pending-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token
                ),
                {'data': {"status": "pending"}}
            )
            self.assertEqual(response.status, '200 OK')

        self.tick(delta=timedelta(days=11))
        self.check_chronograph()

        with open(TARGET_DIR + 'active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token
                )
            )
            self.assertEqual(response.status, '200 OK')
