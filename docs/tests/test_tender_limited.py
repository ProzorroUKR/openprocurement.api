# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.tender.limited.tests.tender import BaseTenderWebTest

from tests.base.test import (
    DumpsWebTestApp,
    MockWebTestMixin,
)
from tests.base.constants import (
    DOCS_URL,
    AUCTIONS_URL,
)
from tests.base.data import (
    test_docs_award,
    test_docs_tender_limited,
    test_docs_lots,
)

test_tender_data = deepcopy(test_docs_tender_limited)
test_lots = deepcopy(test_docs_lots)
award_negotiation = deepcopy(test_docs_award)
test_tender_negotiation_data = deepcopy(test_tender_data)
test_tender_negotiation_quick_data = deepcopy(test_tender_data)

award_negotiation['value']['valueAddedTaxIncluded'] = False
test_tender_negotiation_data['procurementMethodType'] = "negotiation"
test_tender_negotiation_data['cause'] = "twiceUnsuccessful"
test_tender_negotiation_data['causeDescription'] = "оригінальний тендер не вдався двічі"
test_tender_negotiation_data['causeDescription_en'] = "original tender has failed twice"
test_tender_negotiation_data['causeDescription_ru'] = "оригинальный тендер не получился дважды"
test_tender_negotiation_data['value']['valueAddedTaxIncluded'] = False
test_tender_negotiation_quick_data['cause'] = "twiceUnsuccessful"
test_tender_negotiation_quick_data['procurementMethodType'] = "negotiation.quick"
test_tender_negotiation_quick_data['causeDescription'] = "оригінальний тендер не вдався двічі"
test_tender_negotiation_quick_data['causeDescription_en'] = "original tender has failed twice"
test_tender_negotiation_quick_data['causeDescription_ru'] = "оригинальный тендер не получился дважды"
test_lots[0]['value'] = test_tender_negotiation_data['value']

TARGET_DIR = 'docs/source/tendering/limited/http/'


class TenderLimitedResourceTest(BaseTenderWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super(TenderLimitedResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderLimitedResourceTest, self).tearDown()

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tutorial/create-tender-procuringEntity.http', 'wt') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'tutorial/tender-listing-after-procuringEntity.http', 'wt') as self.app.file_obj:
            response = self.app.get('/tenders?opt_pretty=1')
            self.assertEqual(response.status, '200 OK')

        #### Tender activating

        with open(TARGET_DIR + 'tutorial/tender-activating.http', 'wt') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/active-tender-listing-after-procuringEntity.http', 'wt') as self.app.file_obj:
            response = self.app.get('/tenders?opt_pretty=1')
            self.assertEqual(response.status, '200 OK')

        #### Modifying tender

        items = deepcopy(tender["items"])
        items[0].update(
            {
                "quantity": 9,
                "unit": {
                    "code": "MON",
                    "name": "month"
                }
            }
        )
        with open(TARGET_DIR + 'tutorial/patch-items-value-periods.http', 'wt') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {
                    'data':
                        {"items": items}
                }
            )

        with open(TARGET_DIR + 'tutorial/tender-listing-after-patch.http', 'wt') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        #### Uploading documentation

        with open(TARGET_DIR + 'tutorial/upload-tender-notice.http', 'wt') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(
                    self.tender_id, owner_token
                ),
                {
                    "data": {
                        "title": "Notice.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tutorial/update-tender-notice.http', 'wt') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token
                ),
                {
                    "data": {
                        "title": "Notice-2.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        #### Adding supplier information

        with open(TARGET_DIR + 'tutorial/tender-award.http', 'wt') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
                {'data': test_docs_award}
            )
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Uploading Award documentation

        with open(TARGET_DIR + 'tutorial/tender-award-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/documents?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token
                ),
                {
                    "data": {
                        "title": "award_first_document.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/tender-award-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/awards/{}/documents?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token
                )
            )
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-award-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/documents?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token
                ),
                {
                    "data": {
                        "title": "award_second_document.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/tender-award-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/awards/{}/documents?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token
                )
            )
        self.assertEqual(response.status, '200 OK')

        #### Award confirmation

        with open(TARGET_DIR + 'tutorial/tender-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token
                ),
                {'data': {'status': 'active'}}
            )
            self.assertEqual(response.status, '200 OK')

        #### Contracts

        response = self.app.get(
            '/tenders/{}/contracts?acc_token={}'.format(
                self.tender_id, owner_token
            )
        )
        contract = response.json['data'][0]
        self.contract_id = contract['id']
        contract["value"]["amount"] = 238
        contract["value"]["amountNet"] = 230

        ####  Set contract value

        with open(TARGET_DIR + 'tutorial/tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {"data": {"value": contract["value"]}}
            )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        contract["items"][0]["unit"]["value"] = {
            "amount": 12,
            "currency": contract["value"]["currency"],
            "valueAddedTaxIncluded": contract["value"]["valueAddedTaxIncluded"],
        }

        #### Set contact.item.unit value
        with open(TARGET_DIR + 'tutorial/tender-contract-set-contract_items_unit-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {"data": {"items": contract["items"]}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['items'][0]['unit']['value']['amount'], 12)

        # a better way to do same
        item = contract["items"][0]
        with open(TARGET_DIR + 'tutorial/tender-contract_items_unit_value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{self.tender_id}/contracts/{self.contract_id}/items/{item["id"]}/unit/value'
                f'?acc_token={owner_token}',
                {
                    "data": {
                        "amount": 13,
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['amount'], 13)
            self.assertEqual(response.json['data']["currency"], contract["value"]["currency"])
            self.assertEqual(response.json['data']["valueAddedTaxIncluded"], contract["value"]["valueAddedTaxIncluded"])

        #### Setting contract signature date

        with open(TARGET_DIR + 'tutorial/tender-contract-sign-date.http', 'w') as self.app.file_obj:
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
                "startDate": get_now().isoformat(),
                "endDate": (get_now() + timedelta(days=365)).isoformat()
            }
        }
        with open(TARGET_DIR + 'tutorial/tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {'data': {'period': period_dates["period"]}}
            )
        self.assertEqual(response.status, '200 OK')

        #### Uploading Contract documentation

        with open(TARGET_DIR + 'tutorial/tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {
                    "data": {
                        "title": "contract_first_document.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/tender-contract-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                )
            )
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-contract-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {
                    "data": {
                        "title": "contract_second_document.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/tender-contract-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                )
            )
        self.assertEqual(response.status, '200 OK')

        #### Contract signing

        self.tick()

        with open(TARGET_DIR + 'tutorial/tender-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {'data': {'status': 'active'}}
            )
            self.assertEqual(response.status, '200 OK')


class TenderNegotiationLimitedResourceTest(TenderLimitedResourceTest):
    initial_data = test_tender_negotiation_data

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tutorial/create-tender-negotiation-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': self.initial_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']
        self.set_status("active")

        #### Adding supplier information

        with open(TARGET_DIR + 'tutorial/tender-negotiation-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
                {'data': award_negotiation}
            )
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Award confirmation

        with open(TARGET_DIR + 'tutorial/tender-negotiation-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token
                ),
                {
                    'data': {
                        'status': 'active',
                        'qualified': True
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        # get contract
        response = self.app.get(
            '/tenders/{}/contracts?acc_token={}'.format(
                self.tender_id, owner_token
            )
        )
        self.contract_id = response.json['data'][0]['id']

        with open(TARGET_DIR + 'tutorial/negotiation-prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token
                ),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}}
            )
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'tutorial/negotiation-update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token
                ),
                {'data': {'reasonType': 'dateViolation'}}
            )
            self.assertEqual(response.status, '200 OK')

        #### Contract signing

        self.tick()

        tender = self.mongodb.tenders.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.mongodb.tenders.save(tender)

        with open(TARGET_DIR + 'tutorial/tender-negotiation-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {'data': {'status': 'active'}}
            )
            self.assertEqual(response.status, '200 OK')

            #### Preparing the cancellation request

            self.set_status('active')

            with open(TARGET_DIR + 'tutorial/prepare-cancellation.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/tenders/{}/cancellations?acc_token={}'.format(
                        self.tender_id, owner_token
                    ),
                    {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}}
                )
                self.assertEqual(response.status, '201 Created')

            cancellation_id = response.json['data']['id']

            with open(TARGET_DIR + 'tutorial/update-cancellation-reasonType.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/tenders/{}/cancellations/{}?acc_token={}'.format(
                        self.tender_id, cancellation_id, owner_token
                    ),
                    {'data': {'reasonType': 'unFixable'}}
                )
                self.assertEqual(response.status, '200 OK')

            #### Filling cancellation with protocol and supplementary documentation

            with open(TARGET_DIR + 'tutorial/upload-cancellation-doc.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                        self.tender_id, cancellation_id, owner_token
                    ),
                    {
                        "data": {
                            "title": "Notice.pdf",
                            "url": self.generate_docservice_url(),
                            "hash": "md5:" + "0" * 32,
                            "format": "application/pdf",
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
                        "data": {
                            "title": "Notice-2.pdf",
                            "url": self.generate_docservice_url(),
                            "hash": "md5:" + "0" * 32,
                            "format": "application/pdf",
                        }
                    }
                )
                self.assertEqual(response.status, '200 OK')

            #### Activating the request and cancelling tender
            with open(TARGET_DIR + 'tutorial/pending-cancellation.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/tenders/{}/cancellations/{}?acc_token={}'.format(
                        self.tender_id, cancellation_id, owner_token
                    ),
                    {'data': {"status": "pending"}}
                )
                self.assertEqual(response.status, '200 OK')

            self.tick(delta=timedelta(days=11))

            with open(TARGET_DIR + 'tutorial/active-cancellation.http', 'w') as self.app.file_obj:
                response = self.app.get(
                    '/tenders/{}/cancellations/{}?acc_token={}'.format(
                        self.tender_id, cancellation_id, owner_token
                    )
                )
                self.assertEqual(response.status, '200 OK')

    def test_multiple_lots(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules

        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        #### Creating tender
        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': self.initial_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'multiple_lots_tutorial/activating-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{self.tender_id}?acc_token={owner_token}',
                {'data': {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')

        # add lots
        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': test_lots[0]}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {'data': {'items': items}}
            )
            self.assertEqual(response.status, '200 OK')

        while True:
            with open(TARGET_DIR + 'multiple_lots_tutorial/tender-listing-no-auth.http', 'w') as self.app.file_obj:
                self.app.authorization = None
                response = self.app.get(request_path)
                self.assertEqual(response.status, '200 OK')
                if len(response.json['data']):
                    break

        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        #### Adding supplier information
        self.app.authorization = ('Basic', ('broker', ''))
        suspplier_loc = deepcopy({'data': test_docs_award})
        suspplier_loc['data']['lotID'] = lot_id1
        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token),
                suspplier_loc
            )
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Award confirmation

        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token
                ),
                {
                    'data': {
                        'status': 'active',
                        'qualified': True
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        # get contract
        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        ####  Set contract value

        with open(
            TARGET_DIR + 'multiple_lots_tutorial/tender-contract-set-contract-value.http',
            'w'
            ) as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {"data": {"value": {"amount": 238, "amountNet": 230}}}
            )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        #### Contract signing

        self.tick()

        tender = self.mongodb.tenders.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.mongodb.tenders.save(tender)

        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {'data': {'status': 'active'}}
            )
            self.assertEqual(response.status, '200 OK')


class TenderNegotiationQuickLimitedResourceTest(TenderNegotiationLimitedResourceTest):
    initial_data = test_tender_negotiation_quick_data

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure

        self.app.authorization = ('Basic', ('broker', ''))

        with open(
            TARGET_DIR + 'tutorial/create-tender-negotiation-quick-procuringEntity.http',
            'w'
            ) as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': self.initial_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        with open(
            TARGET_DIR + 'multiple_lots_tutorial/activating-negotiation-quick-tender.http', 'w'
            ) as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{self.tender_id}?acc_token={owner_token}',
                {'data': {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')

        #### Adding supplier information

        with open(TARGET_DIR + 'tutorial/tender-negotiation-quick-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(
                    self.tender_id, owner_token
                ),
                {'data': award_negotiation}
            )
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Award confirmation

        with open(TARGET_DIR + 'tutorial/tender-negotiation-quick-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token
                ),
                {'data': {'status': 'active', 'qualified': True}}
            )
            self.assertEqual(response.status, '200 OK')

        # get contract
        response = self.app.get(
            '/tenders/{}/contracts?acc_token={}'.format(
                self.tender_id, owner_token
            )
        )
        self.contract_id = response.json['data'][0]['id']

        #### Contract signing

        self.tick()

        tender = self.mongodb.tenders.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.mongodb.tenders.save(tender)

        with open(TARGET_DIR + 'tutorial/tender-negotiation-quick-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token
                ),
                {'data': {'status': 'active'}}
            )
            self.assertEqual(response.status, '200 OK')
