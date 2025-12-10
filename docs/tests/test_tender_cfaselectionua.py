import os
from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import (
    test_docs_features,
    test_docs_lot_bid,
    test_docs_lot_bid2_with_docs,
    test_docs_lots,
    test_docs_parameters,
    test_docs_tender_cfaselectionua_maximum,
)
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

from openprocurement.api.utils import get_now
from openprocurement.tender.cfaselectionua.tests.base import (
    BaseTenderWebTest,
    test_tender_cfaselectionua_agreement,
    test_tender_cfaselectionua_bids,
    test_tender_cfaselectionua_data,
)

test_tender_cfaselectionua_data = deepcopy(test_tender_cfaselectionua_data)

bid = deepcopy(test_docs_lot_bid)
bid2 = deepcopy(test_docs_lot_bid2_with_docs)
test_features = deepcopy(test_docs_features)
test_agreement = deepcopy(test_tender_cfaselectionua_agreement)
test_agreement['contracts'][0]['suppliers'][0]['scale'] = "large"
test_lots = deepcopy(test_docs_lots)
test_tender_maximum_data = deepcopy(test_docs_tender_cfaselectionua_maximum)

BASE_DIR = 'docs/source/tendering/cfaselectionua/'
TARGET_DIR = BASE_DIR + 'tutorial/'
TARGET_CSV_DIR = BASE_DIR + 'csv/'


class TenderResourceTest(BaseTenderWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_cfaselectionua_data
    initial_bids = test_tender_cfaselectionua_bids
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="closeFrameworkAgreementSelectionUA",
            file_path=TARGET_CSV_DIR + "config.csv",
        )

    def test_docs_allowed_kind_csv(self):
        self.write_allowed_kind_csv(
            pmt="closeFrameworkAgreementSelectionUA",
            file_path=TARGET_CSV_DIR + "kind.csv",
        )

    def test_docs_tutorial(self):
        request_path = '/tenders?opt_pretty=1'

        self.app.authorization = ('Basic', ('broker', ''))

        # Creating tender

        agreement_id = uuid4().hex
        agreements = {'agreements': [{'id': agreement_id}]}

        test_features[0]['relatedItem'] = test_agreement['items'][0]['id']
        test_agreement['features'] = test_features
        for contract in test_agreement['contracts']:
            contract['parameters'] = test_docs_parameters

        lot = deepcopy(test_lots[0])
        lot['id'] = uuid4().hex

        test_tender_cfaselectionua_data.update(agreements)
        test_tender_cfaselectionua_data['lots'] = [lot]
        for item in test_tender_cfaselectionua_data['items']:
            item['relatedLot'] = lot['id']
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat(),
            }

        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {'data': test_tender_cfaselectionua_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        test_tender_maximum_data.update(agreements)
        test_tender_maximum_data['lots'] = [lot]
        test_tender_maximum_data['items'][0]['id'] = uuid4().hex
        test_tender_maximum_data['items'][0]['relatedLot'] = lot['id']

        with open(TARGET_DIR + 'create-tender-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {'data': test_tender_maximum_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        response = self.app.post_json(
            '/tenders?opt_pretty=1', {'data': test_tender_cfaselectionua_data, 'config': self.initial_config}
        )
        self.assertEqual(response.status, '201 Created')

        agreement = deepcopy(test_agreement)
        agreement["_id"] = agreement_id
        agreement['features'] = test_features

        self.create_agreement(agreement)

        with open(TARGET_DIR + 'tender-switch-draft-pending.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'status': 'draft.pending'}}
            )
            data = response.json['data']
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'draft.pending')

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.json['data']['status'], 'active.enquiries')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tender-in-active-enquiries.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.json['data']['status'], 'active.enquiries')
            tender = response.json['data']

        with open(TARGET_DIR + 'initial-tender-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        req_data = test_tender_cfaselectionua_data.copy()
        req_data["agreements"] = [{"id": agreement_id}]
        response = self.app.post_json('/tenders', {'data': req_data, 'config': self.initial_config})
        self.assertEqual((response.status, response.content_type), ('201 Created', 'application/json'))
        self.tender_id = response.json['data']['id']
        self.tender_token = owner_token = response.json['access']['token']

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {'status': 'draft.pending'}}
        )

        self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
        self.assertEqual(response.json['data']['status'], 'draft.pending')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        tender = response.json['data']
        self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
        self.assertEqual(response.json['data']['status'], 'active.enquiries')

        self.app.authorization = ('Basic', ('broker', ''))

        # Modifying tender

        tender_period_end_date = get_now() + timedelta(days=15, seconds=10)
        items = deepcopy(response.json["data"]["items"])
        items[0]["quantity"] = 6
        with open(TARGET_DIR + 'patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {
                    'data': {
                        "tenderPeriod": {
                            "startDate": response.json["data"]["tenderPeriod"]["startDate"],
                            "endDate": tender_period_end_date.isoformat(),
                        },
                        "items": items,
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')

        with open(TARGET_DIR + 'tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        # Setting Bid guarantee

        with open(TARGET_DIR + 'set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], owner_token),
                {"data": {"guarantee": {"amount": 8, "currency": "USD"}}},
            )
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        # Uploading documentation

        with open(TARGET_DIR + 'upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {
                    'data': {
                        'title': 'Notice.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf',
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + 'tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}'.format(self.tender_id, doc_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-document-add-documentType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                {'data': {"documentType": "technicalSpecifications"}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-document-edit-docType-desc.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                {'data': {"description": "document description modified"}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {
                    'data': {
                        'title': 'AwardCriteria.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf',
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                {
                    'data': {
                        'title': 'AwardCriteria.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf',
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # Switch tender to active.tendering

        self.set_status('active.enquiries', start_end='end')
        response = self.check_chronograph()
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        # Registering bid

        self.app.authorization = ('Basic', ('broker', ''))
        bids_access = {}

        bid['parameters'] = test_docs_parameters
        bid['lotValues'][0]['relatedLot'] = lot['id']
        with open(TARGET_DIR + 'register-bidder-invalid.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        bid['tenderers'] = tender['agreements'][0]['contracts'][0]['suppliers']
        with open(TARGET_DIR + 'register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid})
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        lot_values = response.json["data"]["lotValues"]

        with open(TARGET_DIR + 'activate-bidder-without-proposal.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "pending"}},
                status=422,
            )

        with open(TARGET_DIR + 'upload-bid-proposal.http', 'w') as self.app.file_obj:
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
            doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "pending"}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, '200 OK')

        # lot_values = deepcopy(bid["lotValues"])
        lot_values[0]["value"]["amount"] = 510
        with open(TARGET_DIR + 'patch-pending-bid.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {'lotValues': lot_values}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'activate-bidder-without-sign.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "pending"}},
                status=422,
            )

        self.tick_delta = None
        self.tick(timedelta(minutes=1))
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid1_id],
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
            doc_id=doc_id,
        )
        self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
            {'data': {"status": "pending"}},
        )

        # Second bid registration with documents

        bid2['parameters'] = test_docs_parameters
        bid2['lotValues'][0]['relatedLot'] = lot['id']
        bid2['tenderers'] = tender['agreements'][0]['contracts'][1]['suppliers']
        with open(TARGET_DIR + 'register-2nd-bidder.http', 'w') as self.app.file_obj:
            for document in bid2['documents']:
                document['url'] = self.generate_docservice_url()
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid2})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('broker', ''))
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid2_id],
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json)

        bid3 = deepcopy(bid2)
        bid3['tenderers'] = tender['agreements'][0]['contracts'][3]['suppliers']
        for document in bid3['documents']:
            document['url'] = self.generate_docservice_url()
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid3})
        bid3_id = response.json['data']['id']
        bids_access[bid3_id] = response.json['access']['token']
        self.assertEqual(response.status, '201 Created')
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid3_id],
            docs_url=f"/bids/{bid3_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json)

        # Auction

        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        auction_url = '{}/tenders/{}_{}'.format(self.auctions_url, self.tender_id, lot['id'])
        patch_data = {
            'lots': [
                {
                    'auctionUrl': auction_url,
                }
            ],
            'bids': [
                {"id": bid1_id, "lotValues": [{"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid1_id)}]},
                {"id": bid2_id, "lotValues": [{"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid2_id)}]},
                {"id": bid3_id, "lotValues": [{"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid3_id)}]},
            ],
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot['id'], owner_token), {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id])
            )
            self.assertEqual(response.status, '200 OK')

        # Confirming qualification

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot['id']),
            {
                'data': {
                    'bids': [
                        {"id": b["id"], "lotValues": [{"value": b["lotValues"][0]["value"]}]} for b in auction_bids_data
                    ]
                }
            },
        )

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'awards-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open(TARGET_DIR + 'unsuccessful-qualified-award.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful", "qualified": True}},
                status=422,
            )

        with open(TARGET_DIR + 'activate-non-qualified-award.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": False}},
                status=422,
            )

        with open(TARGET_DIR + 'award-notice-document-required.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True}},
                status=422,
            )
        with open(TARGET_DIR + 'award-unsuccessful-notice-document-required.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful", "qualified": False}},
                status=422,
            )
        with open(TARGET_DIR + 'award-add-notice-document.http', 'w') as self.app.file_obj:
            self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")

        with open(TARGET_DIR + 'award-qualification-unsuccessful.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful", "qualified": False}},
                status=403,
            )

        with open(TARGET_DIR + 'award-qualification-active.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True}},
            )

        with open(TARGET_DIR + 'award-qualification-cancelled.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "cancelled"}},
            )

        # get new pending award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
        with open(TARGET_DIR + 'award-qualification-unsuccessful1.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful", "qualified": False}},
            )

        # get new pending award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
        with open(TARGET_DIR + 'confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True}},
            )
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.contract_id = [c for c in response.json['data'] if c['status'] == 'pending'][0]['id']

        # Preparing the cancellation request

        self.set_status('active.awarded')
        with open(TARGET_DIR + 'prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, owner_token),
                {
                    'data': {
                        'reason': 'cancellation reason',
                        'reasonType': 'noDemand',
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        # Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'upload-cancellation-doc.http', 'w') as self.app.file_obj:
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
                },
            )
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {'data': {"description": 'Changed description'}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {
                    'data': {
                        'title': 'Notice.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf',
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        # Activating the request and cancelling tender

        with open(TARGET_DIR + 'active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "active"}},
            )
            self.assertEqual(response.status, '200 OK')
