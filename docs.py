# -*- coding: utf-8 -*-
import json
import os
from copy import deepcopy

import openprocurement.tender.limited.tests.base as base_test
from openprocurement.api.tests.base import PrefixedRequestClass
from openprocurement.tender.limited.tests.tender import BaseTenderWebTest
from webtest import TestApp

test_tender_data = {
        "dateModified": "2016-01-14T16:48:35.636859+02:00",
        "id": "2d06f1999dcf436fb61ccd0168702459",
        "items": [
            {
                "additionalClassifications": [
                    {
                        "description": "Послуги шкільних їдалень",
                        "id": "55.51.10.300",
                        "scheme": "ДКПП"
                    }
                ],
                "classification": {
                    "description": "Послуги з харчування у школах",
                    "id": "55523100-3",
                    "scheme": "CPV"
                },
                "description": "Послуги шкільних їдалень",
                "id": "2dc54675d6364e2baffbc0f8e74432ac"
            }
        ],
        "owner": "broker",
        "procurementMethod": "limited",
        "procurementMethodType": "reporting",
        "status": "active",
        "procuringEntity": {
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
        "value": {
            "amount": 500000,
            "currency": "UAH",
            "valueAddedTaxIncluded": "true"
        },
        "tenderID": "UA-2016-01-14-000003",
        "title": "Послуги шкільних їдалень",
}

supplier = {'data':
    {
        "date": "2016-01-14T18:07:00.628073+02:00",
        "id": "d373338bc3324f14b8b3d4af68922773",
        "status": "pending",
        "suppliers": [
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
                    "id": "13313462",
                    "legalName": "Державне комунальне підприємство громадського харчування «Школяр»",
                    "scheme": "UA-EDR",
                    "uri": "http://sch10.edu.vn.ua/"
                },
                "name": "ДКП «Школяр»"
            }
        ],
        "value": {
            "amount": 475000,
            "currency": "UAH",
            "valueAddedTaxIncluded": "true"
        }
    }
}

cancellation = {
    'data': {
        'reason': 'cancellation reason'
    }
}

test_tender_negotiation_data = deepcopy(test_tender_data)
test_tender_negotiation_data['procurementMethodType'] = "negotiation"

test_tender_negotiation_quick_data = deepcopy(test_tender_data)
test_tender_negotiation_quick_data['procurementMethodType'] = "negotiation.quick"

class DumpsTestAppwebtest(TestApp):

    def do_request(self, req, status=None, expect_errors=None):
        req.headers.environ["HTTP_HOST"] = "api-sandbox.openprocurement.org"
        if not self.file_obj.closed:
            self.file_obj.write(req.as_bytes(True))
            self.file_obj.write("\n")
            if req.body:
                try:
                    self.file_obj.write(
                            '\n' + json.dumps(json.loads(req.body), indent=2, ensure_ascii=False).encode('utf8'))
                    self.file_obj.write("\n")
                except:
                    pass
            self.file_obj.write("\n")
        resp = super(DumpsTestAppwebtest, self).do_request(req, status=status, expect_errors=expect_errors)
        if not self.file_obj.closed:
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


class TenderLimitedResourceTest(BaseTenderWebTest):
    initial_data = test_tender_data

    def setUp(self):
        self.app = DumpsTestAppwebtest(
                "config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure
        #

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/create-tender-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        with open('docs/source/tutorial/tender-listing-after-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders?opt_pretty=1')
            self.assertEqual(response.status, '200 OK')

        #### Modifying tender
        #

        with open('docs/source/tutorial/patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data':
                {"items": [
                    {
                        "quantity": 9,
                        "unit": {
                            "code": "MON",
                            "name": "month"
                            }
                        }]
                    }
                })

        with open('docs/source/tutorial/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        #### Uploading documentation
        #

        with open('docs/source/tutorial/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(
                    self.tender_id, owner_token), upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open('docs/source/tutorial/update-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token), upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        #### Adding supplier information
        #

        with open('docs/source/tutorial/tender-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
                    self.tender_id, owner_token), supplier)
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Uploading Award documentation
        #

        with open('docs/source/tutorial/tender-award-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
                self.tender_id, self.award_id, owner_token), upload_files=[('file', 'award_first_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/tender-award-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards/{}/documents?acc_token={}'.format(
                self.tender_id, self.award_id, owner_token))
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-award-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
                self.tender_id, self.award_id, owner_token), upload_files=[('file', 'award_second_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/tender-award-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards/{}/documents?acc_token={}'.format(
                self.tender_id, self.award_id, owner_token))
        self.assertEqual(response.status, '200 OK')

        #### Award confirmation
        #

        with open('docs/source/tutorial/tender-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token), {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

        #### Contracts
        #

        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(
                self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        #### Uploading Contract documentation
        #

        with open('docs/source/tutorial/tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token), upload_files=[('file', 'contract_first_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/tender-contract-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token))
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-contract-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token), upload_files=[('file', 'contract_second_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/tender-contract-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token))
        self.assertEqual(response.status, '200 OK')

        #### Contract signing
        #

        # tender = self.db.get(self.tender_id)
        # for i in tender.get('awards', []):
            # i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        # self.db.save(tender)

        with open('docs/source/tutorial/tender-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token), {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

        #### Preparing the cancellation request
        #

        self.set_status('active')

        with open('docs/source/tutorial/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token), cancellation)
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        #### Filling cancellation with protocol and supplementary documentation
        #

        with open('docs/source/tutorial/upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), upload_files=[('file', u'Notice.pdf', 'content')])
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token), {'data': {"description": 'Changed description'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token), upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        #### Activating the request and cancelling tender
        #

        with open('docs/source/tutorial/active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), {"data": {"status": "active"}})
            self.assertEqual(response.status, '200 OK')


class TenderNegotiationLimitedResourceTest(TenderLimitedResourceTest):
    initial_data = test_tender_negotiation_data

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure
        #

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/create-tender-negotiation-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {"data": self.initial_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        #### Adding supplier information
        #

        with open('docs/source/tutorial/tender-negotiation-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
                    self.tender_id, owner_token), supplier)
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']


        #### Award confirmation
        #

        with open('docs/source/tutorial/tender-negotiation-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token), {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

        # get contract
        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(
                self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        #### Contract signing
        #

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open('docs/source/tutorial/tender-negotiation-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token), {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')


class TenderNegotiationQuickLimitedResourceTest(TenderNegotiationLimitedResourceTest):
    initial_data = test_tender_negotiation_quick_data

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure
        #

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/create-tender-negotiation-quick-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {"data": self.initial_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        #### Adding supplier information
        #

        with open('docs/source/tutorial/tender-negotiation-quick-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
                    self.tender_id, owner_token), supplier)
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Award confirmation
        #

        with open('docs/source/tutorial/tender-negotiation-quick-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token), {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

        # get contract
        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(
                self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        #### Contract signing
        #

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open('docs/source/tutorial/tender-negotiation-quick-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token), {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

