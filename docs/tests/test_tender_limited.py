import os
from copy import deepcopy
from datetime import timedelta

from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import test_docs_award, test_docs_lots, test_docs_tender_limited
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

from openprocurement.tender.limited.tests.base import (
    test_tender_negotiation_config,
    test_tender_negotiation_quick_config,
)
from openprocurement.tender.limited.tests.tender import BaseTenderWebTest

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
TARGET_CSV_DIR = 'docs/source/tendering/limited/csv/'


class TenderLimitedResourceTest(BaseTenderWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_docs_config_reporting_csv(self):
        self.write_config_pmt_csv(
            pmt="reporting",
            file_path=TARGET_CSV_DIR + "config-reporting.csv",
        )

    def test_docs_config_negotiation_csv(self):
        self.write_config_pmt_csv(
            pmt="negotiation",
            file_path=TARGET_CSV_DIR + "config-negotiation.csv",
        )

    def test_docs_config_negotiation_quick_csv(self):
        self.write_config_pmt_csv(
            pmt="negotiation.quick",
            file_path=TARGET_CSV_DIR + "config-negotiation-quick.csv",
        )

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure

        self.app.authorization = ('Basic', ('broker', ''))
        reporting_data = deepcopy(test_tender_data)
        reporting_data.pop("procurementMethodRationale", None)

        with open(TARGET_DIR + 'tutorial/create-tender-reporting-invalid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {'data': reporting_data, 'config': self.initial_config}, status=422
            )
        reporting_data["cause"] = "marketUnsuccessful"
        reporting_data["causeDescription"] = "Закупівля із застосуванням електронного каталогу не відбулася"

        with open(TARGET_DIR + 'tutorial/create-tender-reporting-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {'data': reporting_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'tutorial/tender-listing-after-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders?opt_pretty=1')
            self.assertEqual(response.status, '200 OK')

        #### Tender activating

        with open(TARGET_DIR + 'tutorial/tender-activating.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/active-tender-listing-after-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders?opt_pretty=1')
            self.assertEqual(response.status, '200 OK')

        #### Modifying tender

        items = deepcopy(tender["items"])
        items[0].update({"quantity": 9, "unit": {"code": "MON", "name": "month"}})
        with open(TARGET_DIR + 'tutorial/patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {"items": items}}
            )

        with open(TARGET_DIR + 'tutorial/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        #### Uploading documentation

        with open(TARGET_DIR + 'tutorial/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
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

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tutorial/update-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                {
                    "data": {
                        "title": "Notice-2.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        #### Adding supplier information

        with open(TARGET_DIR + 'tutorial/tender-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token), {'data': test_docs_award}
            )
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Uploading Award documentation

        with open(TARGET_DIR + 'tutorial/tender-award-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/documents?acc_token={}'.format(self.tender_id, self.award_id, owner_token),
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
                '/tenders/{}/awards/{}/documents?acc_token={}'.format(self.tender_id, self.award_id, owner_token)
            )
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-award-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/documents?acc_token={}'.format(self.tender_id, self.award_id, owner_token),
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
                '/tenders/{}/awards/{}/documents?acc_token={}'.format(self.tender_id, self.award_id, owner_token)
            )
        self.assertEqual(response.status, '200 OK')

        #### Award confirmation

        with open(TARGET_DIR + 'tutorial/tender-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, owner_token),
                {'data': {'status': 'active'}},
            )
            self.assertEqual(response.status, '200 OK')


class TenderNegotiationLimitedResourceTest(TenderLimitedResourceTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config
    initial_lots = deepcopy(test_lots[:1])

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tutorial/create-tender-negotiation-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {'data': self.initial_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']
        self.set_status("active")

        #### Adding supplier information

        award_negotiation["lotID"] = self.initial_lots[0]["id"]
        with open(TARGET_DIR + 'tutorial/tender-negotiation-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token), {'data': award_negotiation}
            )
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Award confirmation

        with open(TARGET_DIR + 'tutorial/tender-negotiation-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, owner_token),
                {'data': {'status': 'active', 'qualified': True}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/negotiation-prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}},
            )
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'tutorial/negotiation-update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {'data': {'reasonType': 'dateViolation'}},
            )
            self.assertEqual(response.status, '200 OK')

    def test_tender_cancellation(self):
        response = self.app.post_json(
            '/tenders?opt_pretty=1', {'data': self.initial_data, 'config': self.initial_config}
        )
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']
        self.set_status('active')

        award_negotiation["lotID"] = self.initial_lots[0]["id"]
        with open(TARGET_DIR + 'tutorial/tender-negotiation-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token), {'data': award_negotiation}
            )
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Award confirmation
        with open(TARGET_DIR + 'tutorial/tender-negotiation-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, owner_token),
                {'data': {'status': 'active', 'qualified': True}},
            )
            self.assertEqual(response.status, '200 OK')

        #### Preparing the cancellation request
        with open(TARGET_DIR + 'tutorial/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}},
            )
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'tutorial/update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {'data': {'reasonType': 'unFixable'}},
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
                },
            )
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {'data': {"description": 'Changed description'}},
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
                },
            )
            self.assertEqual(response.status, '200 OK')

        #### Activating the request and cancelling tender
        with open(TARGET_DIR + 'tutorial/pending-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {'data': {"status": "pending"}},
            )
            self.assertEqual(response.status, '200 OK')

        self.tick(delta=timedelta(days=11))

        with open(TARGET_DIR + 'tutorial/active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token)
            )
            self.assertEqual(response.status, '200 OK')

    def test_multiple_lots(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender

        self.app.authorization = ('Basic', ('broker', ''))

        tender_data = deepcopy(self.initial_data)
        tender_data.pop("lots", None)
        tender_data["items"] = test_tender_negotiation_data["items"]
        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': tender_data, 'config': self.initial_config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # add lots
        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': test_lots[0]}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {'items': items}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'multiple_lots_tutorial/activating-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{self.tender_id}?acc_token={owner_token}', {'data': {"status": "active"}}
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
                '/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token), suspplier_loc
            )
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Award confirmation

        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, owner_token),
                {'data': {'status': 'active', 'qualified': True}},
            )
            self.assertEqual(response.status, '200 OK')


class TenderNegotiationQuickLimitedResourceTest(TenderNegotiationLimitedResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure

        self.app.authorization = ('Basic', ('broker', ''))

        with open(
            TARGET_DIR + 'tutorial/create-tender-negotiation-quick-procuringEntity.http', 'w'
        ) as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {'data': self.initial_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        with open(
            TARGET_DIR + 'multiple_lots_tutorial/activating-negotiation-quick-tender.http', 'w'
        ) as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{self.tender_id}?acc_token={owner_token}', {'data': {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')

        #### Adding supplier information

        award_negotiation["lotID"] = self.initial_lots[0]["id"]
        with open(TARGET_DIR + 'tutorial/tender-negotiation-quick-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token), {'data': award_negotiation}
            )
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Award confirmation

        with open(TARGET_DIR + 'tutorial/tender-negotiation-quick-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, owner_token),
                {'data': {'status': 'active', 'qualified': True}},
            )
            self.assertEqual(response.status, '200 OK')
