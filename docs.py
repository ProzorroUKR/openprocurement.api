
# -*- coding: utf-8 -*-
import json
import os
from copy import deepcopy
from datetime import timedelta, datetime
from time import sleep
from uuid import uuid4

import openprocurement.tender.cfaselectionua.tests.base as base_test
from openprocurement.api.models import get_now
from openprocurement.api.tests.base import PrefixedRequestClass
from openprocurement.tender.cfaselectionua.constants import BOT_NAME
from openprocurement.tender.cfaselectionua.tests.base import (
    BaseTenderWebTest, test_tender_data, test_bids, test_agreement, test_lots
)
from webtest import TestApp

now = datetime.now()
lot_id = uuid4().hex
agreement_id = uuid4().hex


bid = {
    "data": {
        "tenderers": [
            {
                "address": {
                    "countryName": "Україна",
                    "locality": "м. Вінниця",
                    "postalCode": "21100",
                    "region": "м. Вінниця",
                    "streetAddress": "вул. Островського, 33"
                },
                "contactPoint": {
                    "email": "soleksuk@gmail.com",
                    "name": "Сергій Олексюк",
                    "telephone": "+380 (432) 21-69-30"
                },
                "identifier": {
                    "scheme": u"UA-EDR",
                    "id": u"00137256",
                    "uri": u"http://www.sc.gov.ua/"
                },
                "name": "ДКП «Школяр»"
            }
        ],
        "status": "draft",
        "lotValues": [{
            "value": {
                "amount": 500
            },
            "relatedLot": lot_id
        }]
    }
}

bid2 = {
    "data": {
        "tenderers": [
            {
                "address": {
                    "countryName": "Україна",
                    "locality": "м. Львів",
                    "postalCode": "79013",
                    "region": "м. Львів",
                    "streetAddress": "вул. Островського, 34"
                },
                "contactPoint": {
                    "email": "aagt@gmail.com",
                    "name": "Андрій Олексюк",
                    "telephone": "+380 (322) 91-69-30"
                },
                "identifier": {
                    "scheme": u"UA-EDR",
                    "id": u"00137226",
                    "uri": u"http://www.sc.gov.ua/"
                },
                "name": "ДКП «Книга»"
            }
        ],
        "lotValues": [{
            "value": {
                "amount": 499
            },
            "relatedLot": lot_id
        }],
        "documents": [
            {
                'title': u'Proposal_part1.pdf',
                'url': u"http://broken1.ds",
                'hash': 'md5:' + '0' * 32,
                'format': 'application/pdf',
            },
            {
                'title': u'Proposal_part2.pdf',
                'url': u"http://broken2.ds",
                'hash': 'md5:' + '0' * 32,
                'format': 'application/pdf',
            }
        ]
    }
}


cancellation = {
    'data': {
        'reason': 'cancellation reason'
    }
}

test_max_uid = uuid4().hex

test_tender_maximum_data = {
    "title": u"футляри до державних нагород",
    "title_en": u"Cases with state awards",
    "title_ru": u"футляры к государственным наградам",
    "procuringEntity": {
        "name": u"Державне управління справами",
        "identifier": {
            "scheme": u"UA-EDR",
            "id": u"00037256",
            "uri": u"http://www.dus.gov.ua/"
        },
        "address": {
            "countryName": u"Україна",
            "postalCode": u"01220",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова, 11, корпус 1"
        },
        "contactPoint": {
            "name": u"Державне управління справами",
            "telephone": u"0440000000"
        },
        'kind': 'general'
    },
    "items": [
        {
            "id": test_max_uid,
            "description": u"футляри до державних нагород",
            "description_en": u"Cases with state awards",
            "description_ru": u"футляры к государственным наградам",
            "classification": {
                "scheme": u"ДК021",
                "id": u"44617100-9",
                "description": u"Cartons"
            },
            "additionalClassifications": [
                {
                    "scheme": u"ДКПП",
                    "id": u"17.21.1",
                    "description": u"папір і картон гофровані, паперова й картонна тара"
                }
            ],
            "unit": {
                "name": u"item",
                "code": u"44617100-9"
            },
            "quantity": 5
        }
    ],
    "procurementMethodType": "closeFrameworkAgreementSelectionUA",
    "mode": u"test",
}

test_features = [
    {
        "code": "OCDS-123454-AIR-INTAKE",
        "featureOf": "item",
        "relatedItem": test_agreement['items'][0]['id'],
        "title": u"Потужність всмоктування",
        "title_en": "Air Intake",
        "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
        "enum": [
            {
                "value": 0.1,
                "title": u"До 1000 Вт"
            },
            {
                "value": 0.15,
                "title": u"Більше 1000 Вт"
            }
        ]
    },
    {
        "code": "OCDS-123454-YEARS",
        "featureOf": "tenderer",
        "title": u"Років на ринку",
        "title_en": "Years trading",
        "description": u"Кількість років, які організація учасник працює на ринку",
        "enum": [
            {
                "value": 0.05,
                "title": u"До 3 років"
            },
            {
                "value": 0.1,
                "title": u"Більше 3 років, менше 5 років"
            },
            {
                "value": 0.15,
                "title": u"Більше 5 років"
            }
        ]
    }
]


test_complaint_data = {'data':
        {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': bid["data"]["tenderers"][0]
        }
    }

test_lots.append(deepcopy(test_lots[0]))
test_lots[0]['id'] = lot_id
test_lots[1]['title'] = 'Лот №2'
test_lots[1]['description'] = 'Опис Лот №2'

test_tender_data['lots'] = [test_lots[0]]
test_tender_maximum_data['lots'] = [test_lots[0]]
test_tender_data.update({'agreements': [{'id': agreement_id}]})
for item in test_tender_data['items']:
    item['relatedLot'] = lot_id
for item in test_tender_maximum_data['items']:
    item['relatedLot'] = lot_id


class DumpsTestAppwebtest(TestApp):
    def do_request(self, req, status=None, expect_errors=None):
        req.headers.environ["HTTP_HOST"] = "api-sandbox.openprocurement.org"
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            self.file_obj.write(req.as_bytes(True))
            self.file_obj.write("\n")
            if req.body:
                try:
                    self.file_obj.write(
                        '\n' + json.dumps(json.loads(req.body), indent=2, ensure_ascii=False).encode('utf8'))
                    self.file_obj.write("\n")
                except Exception:
                    pass
            self.file_obj.write("\n")
        resp = super(DumpsTestAppwebtest, self).do_request(req, status=status, expect_errors=expect_errors)
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            headers = [(n.title(), v)
                       for n, v in resp.headerlist
                       if n.lower() != 'content-length']
            headers.sort()
            self.file_obj.write(str('\n%s\n%s\n') % (
                resp.status,
                str('\n').join([str('%s: %s') % (n, v) for n, v in headers]),
            ))

            if resp.testbody:
                try:
                    self.file_obj.write(
                        '\n' + json.dumps(json.loads(resp.testbody), indent=2, ensure_ascii=False).encode('utf8'))
                except Exception:
                    pass
            self.file_obj.write("\n\n")
        return resp


class TenderResourceTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_bids = test_bids
    docservice = True

    def setUp(self):
        self.app = DumpsTestAppwebtest(
            "config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db
        if self.docservice:
            self.setUpDS()
            self.app.app.registry.docservice_url = 'http://public.docs-sandbox.openprocurement.org'

    def generate_docservice_url(self):
        return super(TenderResourceTest,
                     self).generate_docservice_url().replace('/localhost/', '/public.docs-sandbox.openprocurement.org/')

    def test_docs_tutorial(self):
        request_path = '/tenders?opt_pretty=1'

        # Exploring basic rules
        #

        with open('docs/source/tutorial/tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        with open('docs/source/tutorial/tender-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=415)
            self.assertEqual(response.status, '415 Unsupported Media Type')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/tender-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post(request_path, 'data', content_type='application/json', status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')

        # Creating tender
        #

        with open('docs/source/tutorial/tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        with open('docs/source/tutorial/blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/create-tender-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_maximum_data})
            self.assertEqual(response.status, '201 Created')

        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data})
        self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/tender-switch-draft-pending.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                           {'data': {'status': 'draft.pending'}})
            data = response.json['data']
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'draft.pending')

        self.app.authorization = ('Basic', (BOT_NAME, ''))

        agreement = deepcopy(test_agreement)
        agreement['features'] = test_features

        response = self.app.patch_json('/tenders/{}/agreements/{}'.format(tender['id'], agreement_id),
                                       {'data': agreement})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'active.enquiries'}})
        self.assertEqual(response.json['data']['status'], 'active.enquiries')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/tender-in-active-enquiries.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.json['data']['status'], 'active.enquiries')
            tender = response.json['data']

        response = self.app.get('/tenders')  # start couchdb index views
        sleep(8)  # wait until couchdb index views complete
        with open('docs/source/tutorial/initial-tender-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json('/tenders', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.tender_id = response.json['data']['id']
        self.tender_token = owner_token = response.json['access']['token']


        response = self.app.patch_json('/tenders/{}?acc_token={}'
                                       .format(self.tender_id, self.tender_token),
                                       {'data': {'agreements': [test_agreement]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}?acc_token={}'
                                       .format(self.tender_id, self.tender_token),
                                       {'data': {'status': 'draft.pending'}})
        tender = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'draft.pending')

        self.app.authorization = ('Basic', (BOT_NAME, ''))

        response = self.app.patch_json('/tenders/{}?acc_token={}'
                                       .format(self.tender_id, self.tender_token),
                                       {'data': {'status': 'active.enquiries'}})
        tender = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.enquiries')

        self.app.authorization = ('Basic', ('broker', ''))

        # Modifying tender
        #

        tenderPeriod_endDate = get_now() + timedelta(days=15, seconds=10)
        with open('docs/source/tutorial/patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data':
                {
                    "tenderPeriod": {
                        "endDate": tenderPeriod_endDate.isoformat()
                    },
                    "items": [{
                        "quantity": 6
                    }]
                }
            })
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')

        with open('docs/source/tutorial/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        # Setting Bid guarantee
        #
        with open('docs/source/tutorial/set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id, owner_token),
                {"data": {"guarantee": {"amount": 8, "currency": "USD"}}})
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        # Uploading documentation
        #

        with open('docs/source/tutorial/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {
                    'title': u'Notice.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open('docs/source/tutorial/tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}'.format(
                self.tender_id, doc_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-document-add-documentType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(
                self.tender_id, doc_id, owner_token), {"data": {"documentType": "technicalSpecifications"}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-document-edit-docType-desc.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(
                self.tender_id, doc_id, owner_token), {"data": {"description": "document description modified"}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {
                    'title': u'AwardCriteria.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open('docs/source/tutorial/tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(
                self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                {'data': {
                    'title': u'AwardCriteria-2.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }}
            )
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(
                self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # Switch tender to active.tendering
        self.set_status('active.enquiries', start_end='end')
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {}})
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        # Registering bid
        #

        self.app.authorization = ('Basic', ('broker', ''))
        bids_access = {}

        with open('docs/source/tutorial/register-bidder-invalid.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        bid['data']['tenderers'] = tender['agreements'][0]['contracts'][0]['suppliers']
        with open('docs/source/tutorial/register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid)
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]), {"data": {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

        # Proposal Uploading
        #

        with open('docs/source/tutorial/upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {
                    'title': u'Proposal.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }}
            )
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        # Second bid registration with documents
        #

        bid2['data']['tenderers'] = tender['agreements'][0]['contracts'][1]['suppliers']
        with open('docs/source/tutorial/register-2nd-bidder.http', 'w') as self.app.file_obj:
            for document in bid2['data']['documents']:
                document['url'] = self.generate_docservice_url()
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid2)
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        bid3 = deepcopy(bid2)
        bid3['data']['tenderers'] = tender['agreements'][0]['contracts'][2]['suppliers']
        for document in bid3['data']['documents']:
            document['url'] = self.generate_docservice_url()
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid3)
        bid3_id = response.json['data']['id']
        bids_access[bid3_id] = response.json['access']['token']
        self.assertEqual(response.status, '201 Created')

        # Auction
        #

        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        patch_data = {
            'lots': [{
                'auctionUrl':
                    u'http://auction-sandbox.openprocurement.org/tenders/{}_{}'.format(self.tender_id, lot_id),
            }],
            'bids': [
                {
                    "id": bid1_id,
                    "lotValues": [{
                        "participationUrl":
                            u'http://auction-sandbox.openprocurement.org/tenders/{}_{}?key_for_bid={}'.format(
                                self.tender_id, lot_id, bid1_id)

                    }]
                },
                {
                    "id": bid2_id,
                    "lotValues": [{
                        "participationUrl":
                            u'http://auction-sandbox.openprocurement.org/tenders/{}_{}?key_for_bid={}'.format(
                                self.tender_id, lot_id, bid2_id
                            )
                    }]
                },
                {
                    "id": bid3_id,
                    "lotValues": [{
                        "participationUrl":
                            u'http://auction-sandbox.openprocurement.org/tenders/{}_{}?key_for_bid={}'.format(
                                self.tender_id, lot_id, bid3_id
                            )
                    }]
                }
            ]
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id, owner_token), {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id]))
            self.assertEqual(response.status, '200 OK')

        # Confirming qualification
        #

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id),
                                      {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/awards-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open('docs/source/tutorial/confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                                {"data": {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.contract_id = response.json['data'][0]['id']

        #  Set contract value
        #

        with open('docs/source/tutorial/tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {"data": {"contractNumber": "contract #13111", "value": {"amount": 238}}}
            )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        # Setting contract signature date
        #

        with open('docs/source/tutorial/tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {'data': {"dateSigned": get_now().isoformat()}}
            )
            self.assertEqual(response.status, '200 OK')

        # Setting contract period
        #

        period_dates = {
            "period": {
                "startDate": (now).isoformat(),
                "endDate": (now + timedelta(days=365)).isoformat()
            }
        }
        with open('docs/source/tutorial/tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {'data': {'period': period_dates["period"]}}
            )
        self.assertEqual(response.status, '200 OK')

        # Uploading contract documentation
        #

        with open('docs/source/tutorial/tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/contracts/{}/documents?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {'data': {
                    'title': u'contract_first_document.doc',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword',
                }}
            )
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/tender-contract-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-contract-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/contracts/{}/documents?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {'data': {
                    'title': u'contract_second_document.doc',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword',
                }}
            )
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/tender-contract-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        # Setting contract signature date
        #

        with open('docs/source/tutorial/tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {'data': {"dateSigned": get_now().isoformat()}}
            )
            self.assertEqual(response.status, '200 OK')

        # Contract signing
        #

        with open('docs/source/tutorial/tender-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token), {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

        # Preparing the cancellation request
        #

        self.set_status('active.awarded')
        with open('docs/source/tutorial/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
                self.tender_id, owner_token), cancellation)
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        # Filling cancellation with protocol and supplementary documentation
        #

        with open('docs/source/tutorial/upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id, cancellation_id,
                                                                             owner_token),
                {'data': {
                    'title': u'Notice.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id, cancellation_id,
                                                                                cancellation_doc_id, owner_token),
                {'data': {"description": 'Changed description'}}
            )
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id, cancellation_id,
                                                                                cancellation_doc_id, owner_token),
                {'data': {
                    'title': u'Notice-2.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }}
            )
            self.assertEqual(response.status, '200 OK')

        # Activating the request and cancelling tender
        #

        with open('docs/source/tutorial/active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')
