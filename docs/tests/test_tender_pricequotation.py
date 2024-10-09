import os
from copy import deepcopy
from datetime import timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

from pyramid.response import Response
from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.tests.base import (
    BaseTenderWebTest,
    test_tender_pq_bids,
    test_tender_pq_bids_with_docs,
    test_tender_pq_category,
    test_tender_pq_criteria_1,
    test_tender_pq_data,
    test_tender_pq_response_1,
    test_tender_pq_short_profile,
    test_tender_pq_shortlisted_firms,
)
from openprocurement.tender.pricequotation.tests.data import test_agreement_pq_data
from openprocurement.tender.pricequotation.tests.utils import (
    copy_criteria_req_id,
    copy_tender_items,
    criteria_drop_uuids,
)

test_tender_data = deepcopy(test_tender_pq_data)
bid_draft = deepcopy(test_tender_pq_bids[0])
bid_draft["status"] = "draft"

TARGET_DIR = 'docs/source/tendering/pricequotation/http/'
TARGET_CSV_DIR = 'docs/source/tendering/pricequotation/csv/'


class TenderResourceTest(BaseTenderWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_bids = test_tender_pq_bids
    freezing_datetime = '2023-10-10T00:00:00+02:00'
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL
    tender_token = None

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="priceQuotation",
            file_path=TARGET_CSV_DIR + "config.csv",
        )

    def activate_tender(self, profile, filename):
        with patch(
            "openprocurement.tender.pricequotation.procedure.state.tender_details.get_tender_profile",
            Mock(status=200, return_value=Mock({"data": profile})),
        ), open(TARGET_DIR + f'{filename}.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
                {"data": {"status": "active.tendering"}},
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")

    def test_docs_tutorial(self):

        request_path = '/tenders?opt_pretty=1'

        self.app.authorization = ('Basic', ('broker', ''))

        # Creating tender

        for item in test_tender_data['items']:
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat(),
            }

        test_tender_data.update(
            {
                "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()},
                "criteria": criteria_drop_uuids(deepcopy(test_tender_pq_criteria_1)),
            }
        )

        with patch(
            "openprocurement.tender.core.procedure.state.tender_details.get_tender_profile",
            Mock(return_value=test_tender_pq_short_profile),
        ), patch(
            "openprocurement.tender.core.procedure.state.tender_details.get_tender_category",
            Mock(return_value=test_tender_pq_category),
        ), open(
            TARGET_DIR + 'tender-post-attempt-json-data.http', 'w'
        ) as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {'data': test_tender_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_token = response.json['access']['token']
        self.tender_id = tender['id']

        with open(TARGET_DIR + 'blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'initial-tender-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        # Modifying tender

        self.tick()

        response = self.app.get(f"/tenders/{self.tender_id}")
        tender = response.json["data"]

        tenderPeriod_endDate = get_now() + timedelta(days=15, seconds=10)
        with open(TARGET_DIR + 'patch-tender-data.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                {
                    'data': {
                        "tenderPeriod": {
                            "startDate": tender["tenderPeriod"]["startDate"],
                            "endDate": tenderPeriod_endDate.isoformat(),
                        }
                    }
                },
            )

        # Activating tender

        profile = deepcopy(test_tender_pq_short_profile)
        self.activate_tender(profile, filename='notice-document-required')

        with open(TARGET_DIR + 'add-notice-document.http', 'w') as self.app.file_obj:
            self.add_sign_doc(self.tender_id, self.tender_token)

        # tender relates to non existed profile
        with patch(
            "openprocurement.api.utils.requests.get",
            Mock(return_value=Response(status_code=404)),
        ), open(TARGET_DIR + 'tender-with-non-existed-profile.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
                {"data": {"status": "active.tendering"}},
                status=404,
            )
            self.assertEqual(response.status, "404 Not Found")

        # tender item has not active profile
        profile["status"] = "hidden"
        self.activate_tender(profile, filename="tender-with-non-active-profile")

        # agreement in profile not equals agreement in tender
        profile["status"] = "active"
        profile["agreementID"] = uuid4().hex
        self.activate_tender(profile, filename="tender-agreement-mismatch-in-profile")

        # terminated agreement
        agreement = deepcopy(test_agreement_pq_data)
        agreement["status"] = "terminated"
        self.mongodb.agreements.save(agreement)
        self.activate_tender(test_tender_pq_short_profile, filename="tender-agreement-terminated")

        # successful activation
        agreement["status"] = "active"
        self.mongodb.agreements.save(agreement)
        with patch(
            "openprocurement.tender.pricequotation.procedure.state.tender_details.get_tender_profile",
            Mock(return_value=test_tender_pq_short_profile),
        ), open(TARGET_DIR + 'tender-active.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
                {"data": {"status": "active.tendering"}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        # Registering bid

        self.app.authorization = ('Basic', ('broker', ''))
        bids_access = {}
        bid_data = deepcopy(bid_draft)
        bid_data["requirementResponses"] = copy_criteria_req_id(tender["criteria"], test_tender_pq_response_1)
        bid_data["items"] = copy_tender_items(tender["items"])
        with open(TARGET_DIR + 'register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid_data})
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'patch-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"value": {"amount": 459}}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "pending"}},
            )
            self.assertEqual(response.status, '200 OK')

        # Bid deletion
        with open(TARGET_DIR + 'register-2nd-bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(f'/tenders/{self.tender_id}/bids', {'data': bid_data})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'delete-2nd-bid.http', 'w') as self.app.file_obj:
            response = self.app.delete(f'/tenders/{self.tender_id}/bids/{bid2_id}?acc_token={bids_access[bid2_id]}')
            self.assertEqual(response.status, '200 OK')

        # try to restore deleted bid
        with open(TARGET_DIR + 'get-deleted-bid.http', 'w') as self.app.file_obj:
            response = self.app.get(
                f'/tenders/{self.tender_id}/bids/{bid2_id}?acc_token={bids_access[bid2_id]}',
                status=404,
            )
            self.assertEqual(response.status, "404 Not Found")
            self.assertEqual(response.content_type, "application/json")

        # Proposal Uploading

        with open(TARGET_DIR + 'upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {
                    'data': {
                        'title': 'Proposal.p7s',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'documentType': 'proposal',
                        'format': 'sign/p7s',
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, '200 OK')

        # activate one more time bid 1 after uploading document
        response = self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
            {'data': {"status": "pending"}},
        )
        self.assertEqual(response.status, '200 OK')

        # Second bid registration with documents
        bid_with_docs_data = deepcopy(test_tender_pq_bids_with_docs)
        bid_with_docs_data["requirementResponses"] = copy_criteria_req_id(tender["criteria"], test_tender_pq_response_1)
        bid_with_docs_data["items"] = copy_tender_items(tender["items"])
        for document in bid_with_docs_data['documents']:
            document['url'] = self.generate_docservice_url()
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid_with_docs_data})
        bid2_id = response.json['data']['id']
        bids_access[bid2_id] = response.json['access']['token']
        self.assertEqual(response.status, '201 Created')
        self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id]),
            {'data': {"status": "pending"}},
        )

        # third bid registration
        bid_with_docs_data["tenderers"][0]["identifier"]["id"] = test_agreement_pq_data["contracts"][1]["suppliers"][0][
            "identifier"
        ]["id"]
        for document in bid_with_docs_data['documents']:
            document['url'] = self.generate_docservice_url()
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid_with_docs_data})
        bid3_id = response.json['data']['id']
        bids_access[bid3_id] = response.json['access']['token']
        self.assertEqual(response.status, '201 Created')
        self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid3_id, bids_access[bid3_id]),
            {'data': {"status": "pending"}},
        )

        # agreement contract validation
        bid_data["tenderers"][0]["identifier"]["id"] = "00037200"
        with open(TARGET_DIR + 'register-bidder-not-member.http', 'w') as self.app.file_obj:
            self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid_data}, status=403)

        # disqualify second supplier from agreement during active.tendering
        agreement["contracts"][1]["status"] = "terminated"
        self.mongodb.agreements.save(agreement)

        self.set_status("active.tendering", 'end')
        self.check_chronograph()

        with open(TARGET_DIR + 'active-tendering-end-bids.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids?acc_token={}'.format(self.tender_id, self.tender_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'awards-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # get pending award
        award = [i for i in response.json['data'] if i['status'] == 'pending'][0]
        award_id = award['id']

        # activate award

        with open(TARGET_DIR + 'unsuccessful-qualified-award.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                {"data": {"status": "unsuccessful", "qualified": True}},
                status=422,
            )

        with open(TARGET_DIR + 'activate-non-qualified-award.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                {"data": {"status": "active", "qualified": False}},
                status=422,
            )

        with open(TARGET_DIR + 'award-active.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                {"data": {"status": "active", "qualified": True}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'awards-listing-after-activation.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # cancel first winner
        with open(TARGET_DIR + 'award-cancelled.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                {"data": {"status": "cancelled"}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'awards-listing-after-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # get new pending award and decline it
        award = [i for i in response.json['data'] if i['status'] == 'pending'][0]
        award_id = award['id']

        with open(TARGET_DIR + 'award-unsuccesful.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                {"data": {"status": "unsuccessful", "qualified": False}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'awards-listing-after-unsuccesful.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # get second bidder pending award
        award = [i for i in response.json['data'] if i['status'] == 'pending'][0]
        award_id = award['id']

        # activate second bidder award
        with open(TARGET_DIR + 'award-active-2.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                {"data": {"status": "active", "qualified": True}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'awards-listing-after-activation-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'contract-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        self.contract_id = [contract for contract in response.json['data'] if contract['status'] == 'pending'][0]['id']

        ####  Set contract value

        # Preparing the cancellation request

        self.set_status('active.awarded')
        with open(TARGET_DIR + 'prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}},
            )
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        # Changing cancellation reasonType

        with open(TARGET_DIR + 'update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, self.tender_token),
                {'data': {'reasonType': 'expensesCut'}},
            )
            self.assertEqual(response.status, '200 OK')

        # Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, self.tender_token
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
                    self.tender_id, cancellation_id, cancellation_doc_id, self.tender_token
                ),
                {'data': {"description": 'Changed description'}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, self.tender_token
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
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, self.tender_token),
                {'data': {"status": "active"}},
            )
            self.assertEqual(response.status, '200 OK')
