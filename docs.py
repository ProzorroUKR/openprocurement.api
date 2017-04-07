# -*- coding: utf-8 -*-
import json
import os
from datetime import timedelta

import openprocurement.tender.openuadefense.tests.base as base_test
from openprocurement.api.models import get_now
from openprocurement.api.tests.base import PrefixedRequestClass
from openprocurement.tender.openuadefense.tests.tender import BaseTenderUAWebTest, test_tender_data
from webtest import TestApp

test_tender_ua_data = {
  "tenderPeriod": {
    "endDate": "2016-02-11T14:04:18.962451"
  },
  "title": "футляри до державних нагород",
  "minimalStep": {
    "currency": "UAH",
    "amount": 35
  },
  "procurementMethodType": "aboveThresholdUA.defense",
  "value": {
    "currency": "UAH",
    "amount": 500
  },
  "procuringEntity": {
    "kind": "defense",
    "address": {
        "countryName": "Україна",
        "locality": "м. Вінниця",
        "postalCode": "21027",
        "region": "м. Вінниця",
        "streetAddress": "вул. Стахурського. 22"
    },
    "contactPoint": {
        "name": "Куца Світлана Валентинівна",
        "telephone": "+380 (432) 46-53-02",
        "url": "http://sch10.edu.vn.ua/"
    },
    "identifier": {
        "id": "21725150",
        "legalName": "Заклад \"Загальноосвітня школа І-ІІІ ступенів № 10 Вінницької міської ради\"",
        "scheme": "UA-EDR"
    },
    "name": "ЗОСШ #10 м.Вінниці"
  },
  "items": [
    {
      "unit": {
        "code": "44617100-9",
        "name": "item"
      },
      "additionalClassifications": [
        {
          "scheme": "ДКПП",
          "id": "17.21.1",
          "description": "Послуги шкільних їдалень"
        }
      ],
      "description": "Послуги шкільних їдалень",
      "deliveryDate": {
            "startDate": (get_now() + timedelta(days=20)).isoformat(),
            "endDate": (get_now() + timedelta(days=50)).isoformat()
      },
      "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1"
      },
      "classification": {
        "scheme": "CPV",
        "id": "37810000-9",
        "description": "Test"
      },
      "quantity": 1
    }
  ]
}

test_tender_ua_data["tenderPeriod"] = {
    "endDate": (get_now() + timedelta(days=16)).isoformat()
}

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
        "subcontractingDetails": "ДКП «книга», Україна, м. Львів, вул. Островського, 33",
        "value": {
            "amount": 500
        },
        'selfEligible': True, 'selfQualified': True,
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
        "value": {
            "amount": 499
        },
        'selfEligible': True, 'selfQualified': True,
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


answer =  {
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


class DumpsTestAppwebtest(TestApp):
    def do_request(self, req, status=None, expect_errors=None):
        req.headers.environ["HTTP_HOST"] = "api-sandbox.openprocurement.org"
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            self.file_obj.write(req.as_bytes(True))
            self.file_obj.write("\n")
            if req.body:
                try:
                    self.file_obj.write(
                            'DATA:\n' + json.dumps(json.loads(req.body), indent=2, ensure_ascii=False).encode('utf8'))
                    self.file_obj.write("\n")
                except:
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
                    self.file_obj.write(json.dumps(json.loads(resp.testbody), indent=2, ensure_ascii=False).encode('utf8'))
                except:
                    pass
            self.file_obj.write("\n\n")
        return resp


class TenderUAResourceTest(BaseTenderUAWebTest):
    initial_data = test_tender_ua_data

    def setUp(self):
        self.app = DumpsTestAppwebtest(
                "config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules
        #

        with  open('docs/source/tutorial/tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        with  open('docs/source/tutorial/tender-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=415)
            self.assertEqual(response.status, '415 Unsupported Media Type')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/tender-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post(
                    request_path, 'data', content_type='application/json', status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')

        #### Creating tender
        #

        with open('docs/source/tutorial/tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_ua_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        with open('docs/source/tutorial/blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Modifying tender
        #

        tenderPeriod_endDate = get_now() + timedelta(days=15, seconds=10)
        with open('docs/source/tutorial/patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data':
                {
                    "tenderPeriod": {
                        "endDate": tenderPeriod_endDate.isoformat()
                    }
                }
            })

        with open('docs/source/tutorial/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')


        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        # Setting Bid guarantee
        #

        with open('docs/source/tutorial/set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
                self.tender_id, owner_token), {"data": {"guarantee": {"amount": 8, "currency": "USD"}}})
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])


        #### Uploading documentation
        #

        with open('docs/source/tutorial/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(
                    self.tender_id, owner_token), upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open('docs/source/tutorial/tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(
                    self.tender_id, owner_token), upload_files=[('file', u'AwardCriteria.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open('docs/source/tutorial/tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents?acc_token={}'.format(
                    self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token), upload_files=[('file', 'AwardCriteria-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(
                    self.tender_id))
            self.assertEqual(response.status, '200 OK')

        #### Enquiries
        #

        with open('docs/source/tutorial/ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(
                self.tender_id), question, status=201)
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

        self.go_to_enquiryPeriod_end()
        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                           {'data': {"value": {'amount': 501.0}}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open('docs/source/tutorial/ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(
                self.tender_id), question, status=403)
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


        #### Registering bid
        #

        bids_access = {}
        with open('docs/source/tutorial/register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(
                    self.tender_id), bid)
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        #### Proposal Uploading
        #

        with open('docs/source/tutorial/upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]), upload_files=[('file', 'Proposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')


        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                           {'data': {"value": {'amount': 501.0}}})
        self.assertEqual(response.status, '200 OK')

        #### Bid invalidation
        #

        with open('docs/source/tutorial/bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        #### Bid confirmation
        #

        with open('docs/source/tutorial/bidder-activate-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]), {'data': {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

        # with open('docs/source/tutorial/bidder-after-activate-bid-tender.http', 'w') as self.app.file_obj:
        #     response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
        #             self.tender_id, bid1_id, bids_access[bid1_id]))
        #     self.assertEqual(response.status, '200 OK')
        # tutorial/register-2nd-bidder.http
        with open('docs/source/tutorial/register-2nd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(
                    self.tender_id), bid2)
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')


        #### Auction
        #
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        patch_data = {
            'auctionUrl': u'http://auction-sandbox.openprocurement.org/tenders/{}'.format(self.tender_id),
            'bids': [
                {
                    "id": bid1_id,
                    "participationUrl": u'http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}'.format(self.tender_id, bid1_id)
                },
                {
                    "id": bid2_id,
                    "participationUrl": u'http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}'.format(self.tender_id, bid2_id)
                }
            ]
        }
        response = self.app.patch_json('/tenders/{}/auction?acc_token={}'.format(self.tender_id, owner_token),
                                           {'data': patch_data})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id]))
            self.assertEqual(response.status, '200 OK')

        #### Confirming qualification
        #
        # self.set_status('active.qualification')
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                      {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open('docs/source/tutorial/confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(
                self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        ####  Set contract value

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open('docs/source/tutorial/tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token), {"data": {"value": {"amount": 238}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        #### Setting contract signature date
        #

        with open('docs/source/tutorial/tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token), {'data': {"dateSigned": get_now().isoformat()} })
            self.assertEqual(response.status, '200 OK')

        #### Setting contract period

        period_dates = {"period": {"startDate": (get_now()).isoformat(), "endDate": (get_now() + timedelta(days=365)).isoformat()}}
        with open('docs/source/tutorial/tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, owner_token), {'data': {'period': period_dates["period"]}})
        self.assertEqual(response.status, '200 OK')

        #### Uploading contract documentation
        #

        with open('docs/source/tutorial/tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token), upload_files=[('file', 'contract_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')
            self.document_id = response.json['data']['id']

        with open('docs/source/tutorial/tender-contract-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        #### Preparing the cancellation request
        #

        with open('docs/source/tutorial/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token), cancellation)
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open('docs/source/tutorial/update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), {"data":{'reasonType': 'unsuccessful'}})
            self.assertEqual(response.status, '200 OK')

        #### Filling cancellation with protocol and supplementary documentation
        #

        with open('docs/source/tutorial/upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), upload_files=[('file', u'Notice.pdf', 'content')])
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token), {'data': {"description": 'Changed description'}} )
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token), upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        #### Activating the request and cancelling tender
        #

        with open('docs/source/tutorial/active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), {"data":{"status":"active"}})
            self.assertEqual(response.status, '200 OK')


        #### Creating tender
        #

        with open('docs/source/tutorial/tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_ua_data})
            self.assertEqual(response.status, '201 Created')

    def test_complaints(self):
        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_ua_data})
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
        complaint3_token = response.json['access']['token']

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
        complaint5_token = response.json['access']['token']

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

    def test_award_complaints(self):
        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_ua_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid)
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid2)
        # switch to active.auction
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')

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

        complaint2_token = response.json['access']['token']
        complaint2_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint3_token = response.json['access']['token']
        complaint3_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint4_token = response.json['access']['token']
        complaint4_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_token = response.json['access']['token']
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
        with open('docs/source/tutorial/award-complaint-satisfied-resolving.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token), {"data": {
                "status": "cancelled"
            }})
            self.assertEqual(response.status, '200 OK')
            new_award_id = response.headers['Location'][-32:]

        award_id = new_award_id
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-submit.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint)
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/award-complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, award_id, response.json['data']['id'], response.json['access']['token']), {"data": {
                "cancellationReason": "Умови виправлено",
                "status": "cancelled"
            }})
            self.assertEqual(response.status, '200 OK')
