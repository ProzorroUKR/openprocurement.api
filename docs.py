# -*- coding: utf-8 -*-
import json
import os
from copy import deepcopy
from datetime import timedelta, datetime
from openprocurement.api.models import get_now
from openprocurement.api.tests.base import PrefixedRequestClass
from time import sleep
from webtest import TestApp
from uuid import uuid4

import openprocurement.tender.cfaua.tests.base as base_test
from openprocurement.tender.cfaua.constants import CLARIFICATIONS_UNTIL_PERIOD
from openprocurement.tender.cfaua.tests.tender import BaseTenderWebTest

test_tender_path = os.path.join('data', 'test_tender.json')
with open(os.path.join(os.path.dirname(base_test.__file__), test_tender_path)) as file_obj:
    test_tender_data = json.load(file_obj)

second_item = deepcopy(test_tender_data['items'][0])
second_item['unit']['code'] = '44617100-8'
test_tender_data['items'] = [test_tender_data['items'][0], second_item]

test_tender_data["tenderPeriod"] = {
    "endDate": (get_now() + timedelta(days=31)).isoformat()
}

lot_id = uuid4().hex
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
        "lotValues": [{
            "value": {
                "amount": 500
            },
            "relatedLot": lot_id
        }],
        "status": "draft",
        "subcontractingDetails": "ДКП «Орфей», Україна",
        'selfEligible': True,
        'selfQualified': True,
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
        'selfEligible': True,
        'selfQualified': True,
    }
}

bid3 = {
    "data": {
        "tenderers": [
            {
                "address": {
                    "countryName": "Україна",
                    "locality": "м. Львів",
                    "postalCode": "79013",
                    "region": "м. Львів",
                    "streetAddress": "вул. Островського, 35"
                },
                "contactPoint": {
                    "email": "fake@mail.com",
                    "name": "Іван Іваненко",
                    "telephone": "+380 (322) 12-34-56"
                },
                "identifier": {
                    "scheme": u"UA-EDR",
                    "id": u"00137226",
                    "uri": u"http://www.sc.gov.ua/"
                },
                "name": "«Снігур»"
            }
        ],
        "lotValues": [{
            "value": {
                "amount": 5
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
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }
        ],
        "eligibilityDocuments": [{
            'title': u'eligibility_doc.pdf',
            'url': u"http://broken3.ds",
            'hash': 'md5:' + '0' * 32,
            'format': 'application/pdf',
        }],
        "financialDocuments": [{
            'title': u'financial_doc.pdf',
            'url': u"http://broken4.ds",
            'hash': 'md5:' + '0' * 32,
            'format': 'application/pdf',
        }],
        "qualificationDocuments": [{
            'title': u'qualification_document.pdf',
            'url': u"http://broken5.ds",
            'hash': 'md5:' + '0' * 32,
            'format': 'application/pdf',
        }],
        'selfEligible': True,
        'selfQualified': True,
    }
}

question = {
    "data": {
        "author": {
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
                "id": "00137226",
                "legalName": "Державне комунальне підприємство громадського харчування «Школяр»",
                "scheme": "UA-EDR",
                "uri": "http://sch10.edu.vn.ua/"
            },
            "name": "ДКП «Школяр»"
        },
        "description": "Просимо додати таблицю потрібної калорійності харчування",
        "title": "Калорійність"
    }
}


answer = {
    "data": {
        "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
    }
}

cancellation = {
    'data': {
        'reason': 'cancellation reason'
    }
}

complaint = {
    "data": {
        "author": {
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
                "id": "13313462",
                "legalName": "Державне комунальне підприємство громадського харчування «Школяр»",
                "scheme": "UA-EDR",
                "uri": "http://sch10.edu.vn.ua/"
            },
            "name": "ДКП «Школяр»"
        },
        "description": "Умови виставлені замовником не містять достатньо інформації, щоб заявка мала сенс.",
        "title": "Недостатньо інформації"
    }
}

test_lots = [
    {
        'id': lot_id,
        'title': 'Лот №1',
        'description': 'Опис Лот №1',
        'value': test_tender_data['value'],
        'minimalStep': test_tender_data['minimalStep'],
    },
    {
        'title': 'Лот №2',
        'description': 'Опис Лот №2',
        'value': test_tender_data['value'],
        'minimalStep': test_tender_data['minimalStep'],
    }
]

test_tender_data['lots'] = [test_lots[0]]
for item in test_tender_data['items']:
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
                        'DATA:\n' + json.dumps(json.loads(req.body), indent=2, ensure_ascii=False).encode('utf8')
                    )
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
            self.file_obj.write(str('Response: %s\n%s\n') % (
                resp.status,
                str('\n').join([str('%s: %s') % (n, v) for n, v in headers]),
            ))

            if resp.testbody:
                try:
                    self.file_obj.write(json.dumps(json.loads(resp.testbody),
                                        indent=2, ensure_ascii=False).encode('utf8'))
                except Exception:
                    pass
            self.file_obj.write("\n\n")
        return resp


class TenderResourceTest(BaseTenderWebTest):
    initial_data = test_tender_data
    docservice = True

    def setUp(self):
        self.app = DumpsTestAppwebtest("config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db
        if self.docservice:
            self.setUpDS()
            self.app.app.registry.docservice_url = 'http://public.docs-sandbox.openprocurement.org'

    def generate_docservice_url(self):
        return super(TenderResourceTest, self).generate_docservice_url().replace(
            '/localhost/', '/public.docs-sandbox.openprocurement.org/'
        )

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        # Exploring basic rules
        #

        with open('docs/source/tutorial/tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        with open('docs/source/tutorial/tender-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=415)
            self.assertEqual(response.status, '415 Unsupported Media Type')

        with open('docs/source/tutorial/tender-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post(request_path, 'data', content_type='application/json', status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')

        # Creating tender
        #
        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        with open('docs/source/tutorial/blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        # Let DB index new tender
        response = self.app.get('/tenders')
        sleep(2)

        with open('docs/source/tutorial/initial-tender-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Modifying tender
        #

        tenderPeriod_endDate = get_now() + timedelta(days=30, seconds=10)
        with open('docs/source/tutorial/patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {
                    'data': {
                        "tenderPeriod": {
                            "endDate": tenderPeriod_endDate.isoformat()
                        }
                    }
                }
            )

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
                {"data": {"guarantee": {"amount": 8, "currency": "USD"}}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        # Uploading documentation
        #

        with open('docs/source/tutorial/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                                     upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open('docs/source/tutorial/tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                                     upload_files=[('file', u'AwardCriteria.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open('docs/source/tutorial/tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                                    upload_files=[('file', 'AwardCriteria-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # Enquiries
        #

        with open('docs/source/tutorial/ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), question, status=201)
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(
                self.tender_id, question_id, owner_token), answer, status=200)
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/list-question.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions'.format(
                self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions/{}'.format(
                self.tender_id, question_id))
            self.assertEqual(response.status, '200 OK')

        self.time_shift('enquiryPeriod_ends')

        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(tender['id'], owner_token))
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                           {'data': {"value": {'amount': 501.0}}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open('docs/source/tutorial/ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), question, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open('docs/source/tutorial/update-tender-after-enqiery-with-update-periods.http', 'w') as self.app.file_obj:
            tenderPeriod_endDate = get_now() + timedelta(days=8)
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data':
                {
                    "value": {
                        "amount": 501,
                        "currency": u"UAH"
                    },
                    "tenderPeriod": {
                        "endDate": tenderPeriod_endDate.isoformat()
                    }
                }
            })
            self.assertEqual(response.status, '200 OK')

        # Registering bid
        #

        bids_access = {}
        with open('docs/source/tutorial/register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid)
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}}
            )
            self.assertEqual(response.status, '200 OK')

        # Proposal Uploading
        #

        with open('docs/source/tutorial/upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal.pdf', 'content')]
            )
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/upload-bid-private-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal_top_secrets.pdf', 'content')]
            )
            self.assertEqual(response.status, '201 Created')
            priv_doc_id = response.json['data']['id']

        # set confidentiality properties
        with open('docs/source/tutorial/mark-bid-doc-private.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                self.tender_id, bid1_id, priv_doc_id, bids_access[bid1_id]), {'data': {
                    'confidentiality': 'buyerOnly',
                    'confidentialityRationale': 'Only our company sells badgers with pink hair.',
                }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]
            ))

        with open('docs/source/tutorial/upload-bid-financial-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(self.tender_id, bid1_id,
                                                                              bids_access[bid1_id]),
                upload_files=[('file', 'financial_doc.pdf', '1000$')]
            )
            self.assertEqual(response.status, '201 Created')

        response = self.app.post(
            '/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(self.tender_id, bid1_id,
                                                                          bids_access[bid1_id]),
            upload_files=[('file', 'financial_doc2.pdf', '1000$')]
        )
        self.assertEqual(response.status, '201 Created')
        # financial_doc_id = response.json['data']['id']

        with open('docs/source/tutorial/bidder-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/upload-bid-eligibility-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/eligibility_documents?acc_token={}'.format(self.tender_id, bid1_id,
                                                                                bids_access[bid1_id]),
                upload_files=[('file', 'eligibility_doc.pdf', 'content')]
            )
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/upload-bid-qualification-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/qualification_documents?acc_token={}'.format(self.tender_id, bid1_id,
                                                                                  bids_access[bid1_id]),
                upload_files=[('file', 'qualification_document.pdf', 'content')]
            )
            self.assertEqual(response.status, '201 Created')
            self.qualification_doc_id = response.json['data']['id']
        #  patch bid document by user
        with open('docs/source/tutorial/upload-bid-qualification-document-proposal-updated.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/bids/{}/qualification_documents/{}?acc_token={}'.format(
                self.tender_id, bid1_id, self.qualification_doc_id, bids_access[bid1_id]),
                upload_files=[('file', 'qualification_document2.pdf', 'content')]
            )
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/bidder-view-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {"value": {'amount': 501.0}}})
        self.assertEqual(response.status, '200 OK')

        # Bid invalidation
        #

        with open('docs/source/tutorial/bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        # Bid confirmation
        #

        with open('docs/source/tutorial/bidder-activate-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]), {'data': {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/register-2nd-bidder.http', 'w') as self.app.file_obj:
            for document in bid3['data']['documents']:
                document['url'] = self.generate_docservice_url()
            for document in bid3['data']['eligibilityDocuments']:
                document['url'] = self.generate_docservice_url()
            for document in bid3['data']['financialDocuments']:
                document['url'] = self.generate_docservice_url()
            for document in bid3['data']['qualificationDocuments']:
                document['url'] = self.generate_docservice_url()
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid2)
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/register-3rd-bidder.http', 'w') as self.app.file_obj:
            for document in bid3['data']['documents']:
                document['url'] = self.generate_docservice_url()
            for document in bid3['data']['eligibilityDocuments']:
                document['url'] = self.generate_docservice_url()
            for document in bid3['data']['financialDocuments']:
                document['url'] = self.generate_docservice_url()
            for document in bid3['data']['qualificationDocuments']:
                document['url'] = self.generate_docservice_url()
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid3)
            bid3_id = response.json['data']['id']
            bids_access[bid3_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/register-4rd-bidder.http', 'w') as self.app.file_obj:
            for document in bid3['data']['documents']:
                document['url'] = self.generate_docservice_url()
            for document in bid3['data']['eligibilityDocuments']:
                document['url'] = self.generate_docservice_url()
            for document in bid3['data']['financialDocuments']:
                document['url'] = self.generate_docservice_url()
            for document in bid3['data']['qualificationDocuments']:
                document['url'] = self.generate_docservice_url()
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid3)
            bid4_id = response.json['data']['id']
            bids_access[bid4_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        # Pre-qualification

        self.set_status('active.pre-qualification')
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.app.authorization = auth

        with open('docs/source/tutorial/qualifications-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
            self.assertEqual(response.status, "200 OK")
            qualifications = response.json['data']
            self.assertEqual(len(qualifications), 4)
            self.assertEqual(qualifications[0]['bidID'], bid1_id)
            self.assertEqual(qualifications[1]['bidID'], bid2_id)
            self.assertEqual(qualifications[2]['bidID'], bid3_id)
            self.assertEqual(qualifications[3]['bidID'], bid4_id)

        with open('docs/source/tutorial/approve-qualification1.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualifications[0]['id'],
                                                                    owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}}
            )
            self.assertEqual(response.status, "200 OK")
        with open('docs/source/tutorial/approve-qualification2.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualifications[1]['id'],
                                                                    owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}}
            )
            self.assertEqual(response.status, "200 OK")

        with open('docs/source/tutorial/approve-qualification4.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualifications[3]['id'],
                                                                    owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}}
            )
            self.assertEqual(response.status, "200 OK")

        with open('docs/source/tutorial/reject-qualification3.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualifications[2]['id'],
                                                                    owner_token),
                {"data": {"status": "unsuccessful"}})
            self.assertEqual(response.status, "200 OK")

        with open('docs/source/tutorial/qualificated-bids-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open('docs/source/tutorial/rejected-bid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid3_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        # active.pre-qualification.stand-still

        with open('docs/source/tutorial/pre-qualification-confirmation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                        {"data": {"status": "active.pre-qualification.stand-still"}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        # Auction

        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        patch_data = {
            'lots': [{
                'auctionUrl':
                    u'http://auction-sandbox.openprocurement.org/tenders/{}_{}'.format(self.tender_id, lot_id)
            }],
            'bids': [
                {
                    "id": bid1_id,
                    "lotValues": [{
                        "participationUrl":
                            u'http://auction-sandbox.openprocurement.org/tenders/{}_{}?key_for_bid={}'.format(
                                self.tender_id, lot_id, bid1_id
                            )
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
                    "id": bid3_id
                },
                {
                    "id": bid4_id,
                    "lotValues": [{
                        "participationUrl":
                            u'http://auction-sandbox.openprocurement.org/tenders/{}_{}?key_for_bid={}'.format(
                                self.tender_id, lot_id, bid4_id
                            )
                    }]
                }

            ]
        }
        response = self.app.patch_json('/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id, owner_token),
                                           {'data': patch_data})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id])
            )
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/bidder4-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid4_id, bids_access[bid4_id])
            )
            self.assertEqual(response.status, '200 OK')

        # Confirming qualification
        #
        # self.set_status('active.qualification')
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id),
                                      {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/qualifications-list.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_ids = [i['id'] for i in response.json['data'] if i['status'] == 'pending']

        with open('docs/source/tutorial/confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_ids[0], owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}}
            )
            self.assertEqual(response.status, '200 OK')

        # Fill Agreement unit prices
        #

        for award_id in award_ids[1:]:
            self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                                {"data": {"status": "active", "qualified": True, "eligible": True}})

        #  patch award to cancelled
        with open('docs/source/tutorial/patch-award-cancelled.http', 'w') as self.app.file_obj:
            self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
                self.tender_id, award_ids[0], owner_token), {"data": {"status": "cancelled"}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualifications-list2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_ids = [i['id'] for i in response.json['data'] if i['status'] == 'pending']

        #  patch pending award to unsuccessful
        with open('docs/source/tutorial/patch-award-unsuccessful.http', 'w') as self.app.file_obj:
            self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
                self.tender_id, award_ids[0], owner_token), {"data": {"status": "unsuccessful"}})
            self.assertEqual(response.status, '200 OK')

        #  patch unsuccessful award to cancelled
        with open('docs/source/tutorial/patch-award-unsuccessful-cancelled.http', 'w') as self.app.file_obj:
            self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
                self.tender_id, award_ids[0], owner_token), {"data": {"status": "cancelled"}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualifications-list3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_ids = [i['id'] for i in response.json['data'] if i['status'] == 'pending']

        with open('docs/source/tutorial/confirm-qualification2.http', 'w') as self.app.file_obj:
            self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
                self.tender_id, award_ids[0], owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        for award_id in award_ids[1:]:
            self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                                {"data": {"status": "active", "qualified": True, "eligible": True}})

        self.set_status('active.awarded')

        with open('docs/source/tutorial/upload-prices-document.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(self.tender_id, bid1_id,
                                                                              bids_access[bid1_id]),
                upload_files=[('file', 'prices.xlsx', '<raw_file_data>')]
            )

        with open('docs/source/tutorial/agreements-list.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
        agreement_id = response.json['data'][0]['id']

        with open('docs/source/tutorial/agreement-contracts-list.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/agreements/{}/contracts?acc_token={}'.format(self.tender_id, agreement_id, owner_token)
            )

        contracts = response.json['data']
        i = 1
        for contract in contracts:
            j = 0.5
            unit_prices = []
            for unit_price in contract['unitPrices']:
                unit_prices.append({'relatedItem': unit_price['relatedItem'], 'value': {'amount': j}})
            with open('docs/source/tutorial/agreement-contract-unitprices{}.http'.format(i), 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(self.tender_id, agreement_id,
                                                                                 contract['id'], owner_token),
                    {'data': {'unitPrices': unit_prices}}
                )
            i += 1

        # Time travel to agreement.contractPeriod.clarificationsUntil
        tender = self.db.get(self.tender_id)
        tender['contractPeriod']['startDate'] = \
            (datetime.now() - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1)).isoformat()
        tender['contractPeriod']['clarificationsUntil'] = (datetime.now() - timedelta(days=1)).isoformat()
        self.db.save(tender)

        # Uploading contract documentation
        #

        with open('docs/source/tutorial/tender-agreement-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/agreements/{}/documents?acc_token={}'.format(self.tender_id, agreement_id, owner_token),
                upload_files=[('file', 'agreement_first_document.doc', 'content')]
            )
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/tender-agreement-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/agreements/{}/documents'.format(self.tender_id, agreement_id))
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-agreement-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/agreements/{}/documents?acc_token={}'.format(self.tender_id, agreement_id, owner_token),
                upload_files=[('file', 'agreement_second_document.doc', 'content')]
            )
            self.assertEqual(response.status, '201 Created')
            self.document_id = response.json['data']['id']

        with open('docs/source/tutorial/tender-agreement-patch-document.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(self.tender_id, agreement_id,
                                                                             self.document_id, owner_token),
                {
                    'data': {
                        "language": 'en',
                        'title_en': 'Title of Document',
                        'description_en': 'Description of Document'
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-agreement-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/agreements/{}/documents'.format(self.tender_id, agreement_id))
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-agreement-get.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, owner_token)
            )
            self.assertEqual(response.status, '200 OK')

        # Agreement signing
        #

        with open('docs/source/tutorial/tender-agreement-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, owner_token),
                {"data": {"dateSigned": get_now().isoformat()}}
            )
        self.assertIn('dateSigned', response.json['data'])

        with open('docs/source/tutorial/tender-agreement-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, owner_token),
                {"data": {"status": "active", "period": base_test.agreement_period}}
            )
        self.assertEqual(response.json['data']['status'], 'active')

        with open('docs/source/tutorial/tender-completed.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'complete')
        # self.contract_id = response.json['data'][0]['id']

        # Rollback agreement signing
        tender = self.db.get(self.tender_id)
        tender['status'] = 'active.tendering'
        tender['agreements'][0]['status'] = 'pending'
        self.db.save(tender)

        # Preparing the cancellation request
        #
        with open('docs/source/tutorial/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, owner_token), cancellation
            )
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open('docs/source/tutorial/update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {"data": {'reasonType': 'unsuccessful'}}
            )
            self.assertEqual(response.status, '200 OK')

        # Filling cancellation with protocol and supplementary documentation
        #

        with open('docs/source/tutorial/upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id, cancellation_id,
                                                                             owner_token),
                upload_files=[('file', u'Notice.pdf', 'content')]
            )
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
            response = self.app.put(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id, cancellation_id,
                                                                                cancellation_doc_id, owner_token),
                upload_files=[('file', 'Notice-2.pdf', 'content2')]
            )
            self.assertEqual(response.status, '200 OK')

        # Activating the request and cancelling tender
        #

        with open('docs/source/tutorial/active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status":"active"}}
            )
            self.assertEqual(response.status, '200 OK')

        # transfer agreement to unsuccessful
        #
        tender = self.db.get(self.tender_id)
        tender['status'] = 'active.awarded'
        tender['agreements'][0]['status'] = 'pending'
        del tender['cancellations']
        self.db.save(tender)

        with open('docs/source/tutorial/agreement-unsuccessful.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(
                self.tender_id, agreement_id, owner_token),
                {"data": {"status": "unsuccessful"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-unsuccessful.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

    def test_complaints(self):
        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        with open('docs/source/tutorial/complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), complaint)
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open('docs/source/tutorial/complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/complaints/{}/documents?acc_token={}'.format(self.tender_id, complaint1_id, complaint1_token),
                                     upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/complaint-claim.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint1_id, complaint1_token), {"data": {"status": "claim"}})
            self.assertEqual(response.status, '200 OK')

        claim = {'data': complaint['data'].copy()}
        claim['data']['status'] = 'claim'
        with open('docs/source/tutorial/complaint-submission-claim.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), claim)
            self.assertEqual(response.status, '201 Created')

        complaint2_token = response.json['access']['token']
        complaint2_id = response.json['data']['id']

        complaint_data = {'data': complaint['data'].copy()}
        complaint_data['data']['status'] = 'pending'
        with open('docs/source/tutorial/complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint3_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), claim)
        self.assertEqual(response.status, '201 Created')
        complaint4_id = response.json['data']['id']
        complaint4_token = response.json['access']['token']

        with open('docs/source/tutorial/complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint1_id, complaint1_token), {"data": {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-answer.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint2_id, owner_token), {"data": {
                "status": "answered",
                "resolutionType": "resolved",
                "resolution": "Виправлено неконкурентні умови"
            }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint4_id, owner_token), {"data": {
            "status": "answered",
            "resolutionType": "invalid",
            "resolution": "Вимога не відповідає предмету закупівлі"
        }})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-satisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint2_id, complaint2_token), {"data": {
                "satisfied": True,
                "status": "resolved"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-escalate.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint4_id, complaint4_token), {"data": {
                "satisfied": False,
                "status": "pending"
            }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint6_id = response.json['data']['id']
        complaint6_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint4_id), {"data": {
                "status": "invalid"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id), {"data": {
                "status": "accepted"
            }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint3_id), {"data": {
            "status": "accepted"
        }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint5_id), {"data": {
            "status": "accepted"
        }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint6_id), {"data": {
            "status": "accepted"
        }})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/complaints/{}/documents'.format(self.tender_id, complaint1_id),
                                     upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id), {"data": {
                "status": "satisfied"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint3_id), {"data": {
                "status": "declined"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint5_id), {"data": {
                "decision": "Тендер скасовується замовником",
                "status": "stopped"
            }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint1_id, owner_token), {"data": {
                "tendererAction": "Умови виправлено",
                "status": "resolved"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint6_id, complaint6_token), {"data": {
                "cancellationReason": "Тендер скасовується замовником",
                "status": "stopping"
            }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint6_id), {"data": {
                "decision": "Тендер скасовується замовником",
                "status": "stopped"
            }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), complaint)
        self.assertEqual(response.status, '201 Created')
        complaint7_id = response.json['data']['id']
        complaint7_token = response.json['access']['token']

        with open('docs/source/tutorial/complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint7_id, complaint7_token), {"data": {
                "cancellationReason": "Умови виправлено",
                "status": "cancelled"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/complaints'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

    def test_qualification_complaints(self):
        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid)
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid_id, bid_token), {"data": {"status": "pending"}})

        # create second and third bid
        self.app.authorization = ('Basic', ('broker', ''))
        for _ in range(2):
            self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid2)

        # Pre-qualification
        self.set_status('active.pre-qualification')
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        qualifications = response.json['data']

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], owner_token),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        qualification_id = qualifications[0]['id']

        with open('docs/source/tutorial/qualification-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, bid_token), complaint)
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open('docs/source/tutorial/qualification-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}'.format(self.tender_id, qualification_id, complaint1_id, complaint1_token),
                                     upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/qualification-complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(self.tender_id, qualification_id, complaint1_id, complaint1_token), {"data": {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        complaint_data = {'data': complaint['data'].copy()}
        complaint_data['data']['status'] = 'pending'
        with open('docs/source/tutorial/qualification-complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, bid_token), complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint2_token = response.json['access']['token']
        complaint2_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint3_token = response.json['access']['token']
        complaint3_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint4_token = response.json['access']['token']
        complaint4_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_token = response.json['access']['token']
        complaint5_id = response.json['data']['id']

        claim = {'data': complaint['data'].copy()}
        claim['data']['status'] = 'claim'
        with open('docs/source/tutorial/qualification-complaint-submission-claim.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, bid_token), claim)
            self.assertEqual(response.status, '201 Created')

        complaint6_token = response.json['access']['token']
        complaint6_id = response.json['data']['id']

        with open('docs/source/tutorial/qualification-complaint-answer.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(self.tender_id, qualification_id, complaint6_id, owner_token), {"data": {
                "status": "answered",
                "resolutionType": "resolved",
                "resolution": "Умови виправлено, вибір переможня буде розгянуто повторно"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-satisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(self.tender_id, qualification_id, complaint6_id, complaint6_token), {"data": {
                "satisfied": True,
            }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, bid_token), claim)
        self.assertEqual(response.status, '201 Created')
        complaint7_token = response.json['access']['token']
        complaint7_id = response.json['data']['id']

        response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(self.tender_id, qualification_id, complaint7_id, owner_token), {"data": {
            "status": "answered",
            "resolutionType": "invalid",
            "resolution": "Вимога не відповідає предмету закупівлі"
        }})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-unsatisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(self.tender_id, qualification_id, complaint7_id, complaint7_token), {"data": {
                "satisfied": False,
            }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, bid_token), complaint)
        self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/qualification-complaint-claim.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(self.tender_id, qualification_id, response.json['data']['id'], response.json['access']['token']), {"data": {
                "status": "claim"
            }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, bid_token), complaint)
        self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/qualification-complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(self.tender_id, qualification_id, response.json['data']['id'], response.json['access']['token']), {"data": {
                "cancellationReason": "Умови виправлено",
                "status": "cancelled"
            }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/qualification-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint2_id), {"data": {
                "status": "invalid"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint1_id), {"data": {
                "status": "accepted"
            }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint3_id), {"data": {
            "status": "accepted"
        }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint4_id), {"data": {
            "status": "accepted"
        }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint5_id), {"data": {
            "status": "accepted"
        }})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/qualifications/{}/complaints/{}/documents'.format(self.tender_id, qualification_id, complaint1_id),
                                     upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/qualification-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint1_id), {"data": {
                "status": "satisfied"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint3_id), {"data": {
                "status": "declined"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint5_id), {"data": {
                "decision": "Тендер скасовується замовником",
                "status": "stopped"
            }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/qualification-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(self.tender_id, qualification_id, complaint1_id, owner_token), {"data": {
                "tendererAction": "Умови виправлено",
                "status": "resolved"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(self.tender_id, qualification_id, complaint4_id, complaint4_token), {"data": {
                "cancellationReason": "Тендер скасовується замовником",
                "status": "stopping"
            }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/qualification-complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint4_id), {"data": {
                "decision": "Тендер скасовується замовником",
                "status": "stopped"
            }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = None
        with open('docs/source/tutorial/qualification-complaints-list.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications/{}/complaints'.format(self.tender_id, qualification_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

    def test_award_complaints(self):
        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid)
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid_id, bid_token), {"data": {"status": "pending"}})
        # create second and third bid
        self.app.authorization = ('Basic', ('broker', ''))
        for _ in range(2):
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid2)

        # Pre-qualification
        self.set_status('active.pre-qualification')
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        qualifications = response.json['data']

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], owner_token),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id),
                           {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')

        self.set_status('active.qualification.stand-still')

        with open('docs/source/tutorial/award-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint)
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open('docs/source/tutorial/award-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(self.tender_id, award_id, complaint1_id, complaint1_token),
                                     upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/award-complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, award_id, complaint1_id, complaint1_token), {"data": {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        complaint_data = {'data': complaint['data'].copy()}
        complaint_data['data']['status'] = 'pending'
        with open('docs/source/tutorial/award-complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint2_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint3_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint4_token = response.json['access']['token']
        complaint4_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_id = response.json['data']['id']

        claim = {'data': complaint['data'].copy()}
        claim['data']['status'] = 'claim'
        with open('docs/source/tutorial/award-complaint-submission-claim.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), claim)
            self.assertEqual(response.status, '201 Created')

        complaint6_token = response.json['access']['token']
        complaint6_id = response.json['data']['id']

        with open('docs/source/tutorial/award-complaint-answer.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, award_id, complaint6_id, owner_token), {"data": {
                "status": "answered",
                "resolutionType": "resolved",
                "resolution": "Умови виправлено, вибір переможня буде розгянуто повторно"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-satisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, award_id, complaint6_id, complaint6_token), {"data": {
                "satisfied": True,
            }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), claim)
        self.assertEqual(response.status, '201 Created')
        complaint7_token = response.json['access']['token']
        complaint7_id = response.json['data']['id']

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, award_id, complaint7_id, owner_token), {"data": {
            "status": "answered",
            "resolutionType": "invalid",
            "resolution": "Вимога не відповідає предмету закупівлі"
        }})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-unsatisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, award_id, complaint7_id, complaint7_token), {"data": {
                "satisfied": False,
            }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint)
        self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/award-complaint-claim.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, award_id, response.json['data']['id'], response.json['access']['token']), {"data": {
                "status": "claim"
            }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/award-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint2_id), {"data": {
                "status": "invalid"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id), {"data": {
                "status": "accepted"
            }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint3_id), {"data": {
            "status": "accepted"
        }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint4_id), {"data": {
            "status": "accepted"
        }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint5_id), {"data": {
            "status": "accepted"
        }})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents'.format(self.tender_id, award_id, complaint1_id),
                                     upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/award-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id), {"data": {
                "status": "satisfied"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint3_id), {"data": {
                "status": "declined"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint5_id), {"data": {
                "decision": "Тендер скасовується замовником",
                "status": "stopped"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/award-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, award_id, complaint1_id, owner_token), {"data": {
                "tendererAction": "Умови виправлено, вибір переможня буде розгянуто повторно",
                "status": "resolved"
            }})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, award_id, complaint4_id, complaint4_token), {"data": {
                "cancellationReason": "Тендер скасовується замовником",
                "status": "stopping"
            }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/award-complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint4_id), {"data": {
                "decision": "Тендер скасовується замовником",
                "status": "stopped"
            }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        awards_len = len(response.json['data'])

        with open('docs/source/tutorial/award-complaint-satisfied-resolving.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token), {"data": {
                "status": "cancelled"
            }})
            self.assertEqual(response.status, '200 OK')
        
        self.app.authorization = ('Basic', ('broker', ''))
        get_response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = get_response.json['data'][awards_len]['id']
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        self.set_status('active.qualification.stand-still')

        with open('docs/source/tutorial/award-complaint-submit.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint)
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/award-complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, award_id, response.json['data']['id'], response.json['access']['token']), {"data": {
                "cancellationReason": "Умови виправлено",
                "status": "cancelled"
            }})
            self.assertEqual(response.status, '200 OK')
