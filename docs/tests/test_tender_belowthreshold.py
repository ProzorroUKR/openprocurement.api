# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from uuid import uuid4
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest,
    test_tender_below_bids,
    test_tender_below_lots,
)

from tests.base.test import (
    DumpsWebTestApp,
    MockWebTestMixin,
)
from tests.base.constants import (
    DOCS_URL,
    AUCTIONS_URL,
)
from tests.base.data import (
    test_docs_bid_draft,
    test_docs_bid2_with_docs,
    test_docs_question,
    test_docs_tender_below,
    test_docs_tender_below_maximum,
    test_docs_funder,
)
from tests.test_tender_config import TenderConfigCSVMixin

from openprocurement.tender.belowthreshold.tests.utils import set_bid_lotvalues, set_tender_lots
from openprocurement.tender.core.procedure.utils import dt_from_iso

test_tender_data = deepcopy(test_docs_tender_below)

TARGET_DIR = 'docs/source/tendering/belowthreshold/http/'
TARGET_CSV_DIR = 'docs/source/tendering/belowthreshold/csv/'


class TenderResourceTest(BaseTenderWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_bids = test_tender_below_bids
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super(TenderResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderResourceTest, self).tearDown()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="belowThreshold",
            file_path=TARGET_CSV_DIR + "config.csv",
        )

    def test_docs_2pc(self):
        self.app.authorization = ('Basic', ('broker', ''))

        # Creating tender in draft status

        data = test_tender_data.copy()
        data['status'] = 'draft'

        with open(TARGET_DIR + 'tutorial/tender-post-2pc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']
        # add lots
        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender["id"], owner_token),
            {'data': test_tender_below_lots[0]}
        )
        self.assertEqual(response.status, '201 Created')

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = response.json['data']['id']
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender["id"], owner_token),
            {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        # switch to 'active.enquiries'

        with open(TARGET_DIR + 'tutorial/tender-patch-2pc.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"status": 'active.enquiries'}}
            )
            self.assertEqual(response.status, '200 OK')

    def test_docs_tutorial(self):

        request_path = '/tenders?opt_pretty=1'

        # Invalid request

        with open(TARGET_DIR + 'tutorial/tender-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post_json(
                request_path, {}, content_type='application/json', status=422
            )
            self.assertEqual(response.status, '422 Unprocessable Entity')

        # Creating tender

        with open(TARGET_DIR + 'tutorial/tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        with open(TARGET_DIR + 'tutorial/blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/initial-tender-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        test_docs_tender_below_maximum['items'][0]['id'] = uuid4().hex
        for feature in test_docs_tender_below_maximum['features']:
            if feature['featureOf'] == 'item':
                feature['relatedItem'] = test_docs_tender_below_maximum['items'][0]['id']

        # add lots
        with open(TARGET_DIR + 'tutorial/tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(self.tender_id, owner_token),
                {'data': test_tender_below_lots[0]}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id = response.json['data']['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        with open(TARGET_DIR + 'tutorial/tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {"data": {"items": items}}
            )
            self.assertEqual(response.status, '200 OK')

        tender_lots = response.json["data"]["lots"]

        # Tender activating

        with open(TARGET_DIR + 'tutorial/tender-activating.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"status": "active.enquiries"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/active-tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
        self.app.authorization = ('Basic', ('broker', ''))

        # Create second tender

        set_tender_lots(test_docs_tender_below_maximum, tender_lots)
        self.initial_bids = deepcopy(self.initial_bids)
        for bid in self.initial_bids:
            set_bid_lotvalues(bid, tender_lots)
        with open(TARGET_DIR + 'tutorial/create-tender-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_docs_tender_below_maximum, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(response.json["data"]["id"], response.json["access"]["token"]),
            {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        test_tender_funders_data = deepcopy(test_tender_data)
        test_tender_funders_data['funders'] = [test_docs_funder]
        with open(TARGET_DIR + 'tutorial/create-tender-funders.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_funders_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data, 'config': self.initial_config}
        )
        tender = response.json["data"]
        tender_2_owner_token = response.json['access']['token']
        self.assertEqual(response.status, '201 Created')
        # add lots
        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender["id"], tender_2_owner_token),
            {'data': test_tender_below_lots[0]}
        )
        self.assertEqual(response.status, '201 Created')

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = response.json['data']['id']
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender["id"], tender_2_owner_token),
            {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(response.json["data"]["id"], tender_2_owner_token),
            {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-listing-after-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Modifying tender

        self.tick()

        response = self.app.get(f"/tenders/{self.tender_id}")
        tender = response.json["data"]

        tender_period_end_date = get_now() + timedelta(days=15, seconds=10)
        with open(TARGET_DIR + 'tutorial/patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {
                    'data': {
                        "tenderPeriod": {
                            "startDate": tender["tenderPeriod"]["startDate"],
                            "endDate": tender_period_end_date.isoformat(),
                        }
                    }
                }
            )

        with open(TARGET_DIR + 'tutorial/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Setting funders

        with open(TARGET_DIR + 'tutorial/patch-tender-funders.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"funders": [test_docs_funder]}}
            )
            self.assertIn('funders', response.json['data'])
            self.assertEqual(response.status, '200 OK')

        # Setting Bid guarantee

        with open(TARGET_DIR + 'tutorial/set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {"guarantee": {"amount": 8, "currency": "USD"}}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        # Uploading documentation

        with open(TARGET_DIR + 'tutorial/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {
                    'data': {
                        'title': 'Notice.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf',
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + 'tutorial/tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/documents/{}'.format(
                    self.tender_id, doc_id
                )
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-document-add-documentType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token
                ),
                {'data': {"documentType": "technicalSpecifications"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-document-edit-docType-desc.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token
                ),
                {'data': {"description": "document description modified"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {
                    'data': {
                        'title': 'AwardCriteria.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf',
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tutorial/tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/documents'.format(
                    self.tender_id
                )
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                {
                    'data': {
                        'title': 'AwardCriteria-2.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf',
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/documents'.format(
                    self.tender_id
                )
            )
            self.assertEqual(response.status, '200 OK')

        # Enquiries

        with open(TARGET_DIR + 'tutorial/ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {"data": test_docs_question}, status=201
            )
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/questions/{}?acc_token={}'.format(
                    self.tender_id, question_id, owner_token
                ),
                {
                    "data": {
                        "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
                    }
                }, status=200
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/list-question.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/questions'.format(
                    self.tender_id
                )
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/questions/{}'.format(
                    self.tender_id, question_id
                )
            )
            self.assertEqual(response.status, '200 OK')

        # Patch tenderPeriod in active.tendering status
        self.set_status('active.tendering')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get(f"/tenders/{self.tender_id}")
        tender = response.json["data"]
        self.tick(delta=timedelta(days=6))
        with open(TARGET_DIR + 'tutorial/update-tender-after-enquiry.http', 'w') as self.app.file_obj:
            tender_period_end_date = dt_from_iso(tender["tenderPeriod"]["endDate"]) + timedelta(days=1)
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"value": {'amount': 501.0}, "tenderPeriod": {"endDate": tender_period_end_date.isoformat()}}},
                status=403,
            )
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'tutorial/update-tender-after-enquiry-with-update-periods.http', 'w') as self.app.file_obj:
            tender_period_end_date = dt_from_iso(tender["tenderPeriod"]["endDate"]) + timedelta(days=4)
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {
                    "value": {
                        "amount": 501,
                        "currency": "UAH"
                    },
                    "tenderPeriod": {
                        "endDate": tender_period_end_date.isoformat()
                    }
                }})
            self.assertEqual(response.status, '200 OK')

        # Registering bid
        bids_access = {}
        bid_data = deepcopy(test_docs_bid_draft)
        set_bid_lotvalues(bid_data, tender_lots)
        with open(TARGET_DIR + 'tutorial/register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid_data}
            )
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]
                ),
                {'data': {"status": "pending"}}
            )
            self.assertEqual(response.status, '200 OK')

        # Proposal Uploading

        with open(TARGET_DIR + 'tutorial/upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]
                ),
                {
                    'data': {
                        'title': 'Proposal.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf',
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]
                )
            )
            self.assertEqual(response.status, '200 OK')

        # Second bid registration with documents

        bid_with_docs = deepcopy(test_docs_bid2_with_docs)
        set_bid_lotvalues(bid_with_docs, tender_lots)
        with open(TARGET_DIR + 'tutorial/register-2nd-bidder.http', 'w') as self.app.file_obj:
            for document in bid_with_docs['documents']:
                document['url'] = self.generate_docservice_url()
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid_with_docs}
            )
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

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
            'bids': [{
                "id": bid1_id,
                "lotValues": [
                    {"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid1_id)}
                ]
            }, {
                "id": bid2_id,
                "lotValues": [
                    {"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid2_id)},
                ]
            }]
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id, owner_token),
            {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tutorial/auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id])
            )
            self.assertEqual(response.status, '200 OK')

        # Confirming qualification

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot_id),
            {
                'data': {
                    'bids': [
                        {
                            "id": b["id"],
                            "lotValues": [
                                {"value": lot["value"], "relatedLot": lot["relatedLot"]}
                                for lot in b["lotValues"]
                            ]
                        }
                        for b in auction_bids_data
                    ]
                }
            }
        )

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))

        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open(TARGET_DIR + 'tutorial/confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.contract_id = response.json['data'][0]['id']

        # Preparing the cancellation request

        self.set_status('active.awarded')
        with open(TARGET_DIR + 'tutorial/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token
                ),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}}
            )
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        # Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'tutorial/upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token
                ),
                {
                    'data': {
                        'title': 'Notice.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf',
                    }
                }
            )
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {'data': {"description": 'Changed description'}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {
                    'data': {
                        'title': 'Notice-2.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf',
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        # Activating the request and cancelling tender

        with open(TARGET_DIR + 'tutorial/active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token
                ),
                {'data': {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')
