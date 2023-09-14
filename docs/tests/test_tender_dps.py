import os
import datetime
from copy import deepcopy
from uuid import uuid4

from openprocurement.api.context import get_now
from openprocurement.framework.dps.tests.base import (
    test_framework_dps_data,
    test_framework_dps_config,
    test_submission_data,
    test_submission_config,
)
from openprocurement.tender.core.tests.base import test_exclusion_criteria, test_language_criteria
from openprocurement.tender.open.tests.base import test_tender_dps_config, BaseTenderUAWebTest

from tests.base.constants import DOCS_URL, AUCTIONS_URL
from tests.base.data import (
    test_docs_lots,
    test_docs_tender_dps,
)
from tests.base.test import MockWebTestMixin, DumpsWebTestApp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(BASE_DIR, 'source/tendering/dps/http/')


class TenderResourceTest(
    BaseTenderUAWebTest,
    MockWebTestMixin,
):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super(TenderResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderResourceTest, self).tearDown()
    def create_framework(self):
        response = self.app.post_json("/frameworks", {
            "data": test_framework_dps_data,
            "config": test_framework_dps_config,
        })
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
            {"data": {"status": "active"}}
        )
        self.assertEqual(response.status, "200 OK")
        return response

    def create_submission(self):
        data = deepcopy(test_submission_data)
        data["frameworkID"] = self.framework_id
        data["tenderers"][0]["identifier"]["id"] = uuid4().hex
        response = self.app.post_json("/submissions", {
            "data": data,
            "config": test_submission_config,
        })
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
        response = self.app.post(
            "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
            upload_files=[("file", "name  name.doc", b"content")]
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

        self.create_submission()
        self.activate_submission()
        self.activate_qualification()

        response = self.get_framework()
        self.agreement_id = response.json["data"]["agreementID"]

        # View agreement

        with open(TARGET_DIR + 'view-agreement-1-contract.http', 'w') as self.app.file_obj:
            response = self.app.get("/agreements/{}".format(self.agreement_id))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Creating tender

        data = deepcopy(test_docs_tender_dps)
        data["items"] = [data["items"][0]]
        data["procurementMethodType"] = "dynamicPurchasingSystem"
        data['procuringEntity']['identifier']['id'] = test_framework_dps_data['procuringEntity']['identifier']['id']

        data['agreements'] = [{'id': self.agreement_id}]

        lot = deepcopy(test_docs_lots[0])
        lot['value'] = data['value']
        lot['minimalStep'] = data['minimalStep']
        lot['id'] = uuid4().hex

        data['lots'] = [lot]

        config = deepcopy(test_tender_dps_config)

        for item in data['items']:
            item['relatedLot'] = lot['id']
            item['deliveryDate'] = {
                "startDate": (get_now() + datetime.timedelta(days=2)).isoformat(),
                "endDate": (get_now() + datetime.timedelta(days=5)).isoformat()
            }

        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # add lots

        with open(TARGET_DIR + 'tender-add-lot-more-than-1-error.http', 'w') as self.app.file_obj:
            lot2 = deepcopy(test_docs_lots[1])
            lot2['value'] = data['value']
            lot2['minimalStep'] = data['minimalStep']
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': lot2},
                status=422
            )
            self.assertEqual(response.status, '422 Unprocessable Entity')
            self.assertEqual(
                response.json['errors'][0]['description'],
                "Can't create more than 1 lots"
            )

        # add relatedLot for item

        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = tender["lots"][0]["id"]
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

        # Tender activating (fail)

        with open(TARGET_DIR + 'tender-activating-insufficient-active-contracts-error.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {'data': {"status": "active.tendering"}},
                status=422
            )
            self.assertEqual(response.status, '422 Unprocessable Entity')
            self.assertEqual(
                response.json['errors'][0]['description'],
                "agreements[0] has less than 3 active contracts"
            )

        # Add agreement contracts

        self.app.authorization = ('Basic', ('broker', ''))

        self.create_submission()
        self.activate_submission()
        self.activate_qualification()

        self.create_submission()
        self.activate_submission()
        self.activate_qualification()

        # Tender activating

        with open(TARGET_DIR + 'tender-activating.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {'data': {"status": "active.tendering"}}
            )
            self.assertEqual(response.status, '200 OK')
