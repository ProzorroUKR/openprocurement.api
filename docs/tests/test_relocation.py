# -*- coding: utf-8 -*-
import os

from copy import deepcopy
from datetime import timedelta
from uuid import uuid4
from hashlib import sha512

from openprocurement.api.tests.base import BaseWebTest
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_data,
    test_tender_below_config,
)
from openprocurement.contracting.api.tests.base import test_contract_data
from openprocurement.framework.cfaua.tests.base import test_agreement_data
from openprocurement.planning.api.tests.base import test_plan_data
from openprocurement.api.models import get_now

from tests.base.test import (
    DumpsWebTestApp,
    MockWebTestMixin,
)


class TransferDocsTest(BaseWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        super(TransferDocsTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TransferDocsTest, self).tearDown()

    def test_tenders_docs(self):
        data = deepcopy(test_tender_below_data)

        now = get_now()
        for item in data['items']:
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat()
            }
        data.update(
            {
                "enquiryPeriod": {"endDate": (now + timedelta(days=7)).isoformat()},
                "tenderPeriod": {"endDate": (now + timedelta(days=14)).isoformat()}
            }
        )

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/relocation/tutorial/create-tender.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {
                "data": data,
                "config": test_tender_below_config,
            })
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = tender['id']
        owner_token = response.json['access']['token']
        orig_tender_transfer_token = response.json['access']['transfer']

        self.app.authorization = ('Basic', ('broker2', ''))

        response = self.app.post_json('/transfers', {"data": {}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        transfer = response.json['data']
        access = response.json['access']
        new_access_token = access['token']
        new_transfer_token = access['transfer']

        with open('docs/source/relocation/tutorial/change-tender-ownership-forbidden.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/ownership'.format(tender_id),
                {"data": {"id": transfer['id'], 'transfer': orig_tender_transfer_token}}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(
                response.json['errors'][0]['description'],
                'Broker Accreditation level does not permit ownership change'
            )

        self.app.authorization = ('Basic', ('broker1', ''))

        with open('docs/source/relocation/tutorial/create-tender-transfer.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/transfers', {"data": {}})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            transfer = response.json['data']
            access = response.json['access']
            new_access_token = access['token']
            new_transfer_token = access['transfer']

        with open('docs/source/relocation/tutorial/get-tender-transfer.http', 'w') as self.app.file_obj:
            response = self.app.get('/transfers/{}'.format(transfer['id']))

        with open('docs/source/relocation/tutorial/change-tender-ownership.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/ownership'.format(tender_id),
                {"data": {"id": transfer['id'], 'transfer': orig_tender_transfer_token}}
            )
            self.assertEqual(response.status, '200 OK')
            tender = response.json['data']
            self.assertNotIn('transfer', tender)
            self.assertNotIn('transfer_token', tender)
            self.assertEqual('broker1', tender['owner'])

        with open('docs/source/relocation/tutorial/get-used-tender-transfer.http', 'w') as self.app.file_obj:
            response = self.app.get('/transfers/{}'.format(transfer['id']))

        with open('docs/source/relocation/tutorial/modify-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, new_access_token),
                {"data": {"description": "broker1 now can change the tender"}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['description'], 'broker1 now can change the tender')

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json('/transfers', {"data": {}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        transfer = response.json['data']
        access = response.json['access']
        new_access_token = access['token']
        new_transfer_token = access['transfer']

        with open(
            'docs/source/relocation/tutorial/change-tender-ownership-forbidden-owner.http', 'w'
            ) as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/ownership'.format(tender_id),
                {"data": {"id": transfer['id'], 'transfer': orig_tender_transfer_token}}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(
                response.json['errors'][0]['description'],
                'Owner Accreditation level does not permit ownership change'
            )

    def test_contracts_docs(self):
        test_tender_token = uuid4().hex
        data = deepcopy(test_contract_data)
        data.update(
            {
                "dateSigned": get_now().isoformat(),
                "id": uuid4().hex,
                "tender_id": uuid4().hex,
                "tender_token": sha512(test_tender_token.encode()).hexdigest()
            }
        )
        tender_token = data['tender_token']
        self.app.authorization = ('Basic', ('contracting', ''))

        response = self.app.post_json('/contracts', {'data': data})
        self.assertEqual(response.status, '201 Created')
        contract = response.json['data']
        self.assertEqual('broker', contract['owner'])
        contract_id = contract['id']

        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/relocation/tutorial/get-contract-credentials.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/contracts/{}/credentials?acc_token={}'.format(contract_id, tender_token),
                {'data': ''}
            )
            self.assertEqual(response.status, '200 OK')
            access = response.json['access']
            token = access['token']
            contract_transfer = access['transfer']

        self.app.authorization = ('Basic', ('broker2', ''))

        response = self.app.post_json('/transfers', {"data": {}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        transfer = response.json['data']
        access = response.json['access']
        new_access_token = access['token']
        new_transfer_token = access['transfer']

        with open('docs/source/relocation/tutorial/change-contract-ownership-forbidden.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/contracts/{}/ownership'.format(contract_id),
                {"data": {"id": transfer['id'], 'transfer': contract_transfer}}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(
                response.json['errors'][0]['description'],
                'Broker Accreditation level does not permit ownership change'
            )

        self.app.authorization = ('Basic', ('broker3', ''))

        with open('docs/source/relocation/tutorial/create-contract-transfer.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/transfers', {"data": {}})
            self.assertEqual(response.status, '201 Created')
            transfer = response.json['data']
            self.assertIn('date', transfer)
            transfer_creation_date = transfer['date']
            access = response.json['access']
            new_access_token = access['token']
            new_transfer_token = access['transfer']

        with open('docs/source/relocation/tutorial/change-contract-ownership.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/contracts/{}/ownership'.format(contract_id),
                {"data": {"id": transfer['id'], 'transfer': contract_transfer}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertNotIn('transfer', response.json['data'])
            self.assertNotIn('transfer_token', response.json['data'])
            self.assertEqual('broker3', response.json['data']['owner'])

        with open('docs/source/relocation/tutorial/modify-contract.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/contracts/{}?acc_token={}'.format(contract_id, new_access_token),
                {"data": {"description": "broker3 now can change the contract"}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['description'], 'broker3 now can change the contract')

        with open('docs/source/relocation/tutorial/get-used-contract-transfer.http', 'w') as self.app.file_obj:
            response = self.app.get('/transfers/{}'.format(transfer['id']))

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json('/transfers', {"data": {}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        transfer = response.json['data']
        access = response.json['access']
        new_access_token = access['token']
        new_transfer_token = access['transfer']

        with open(
            'docs/source/relocation/tutorial/change-contract-ownership-forbidden-owner.http', 'w'
            ) as self.app.file_obj:
            response = self.app.post_json(
                '/contracts/{}/ownership'.format(contract_id),
                {"data": {"id": transfer['id'], 'transfer': contract_transfer}}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(
                response.json['errors'][0]['description'],
                'Owner Accreditation level does not permit ownership change'
            )

    def test_plans_docs(self):
        data = deepcopy(test_plan_data)

        now = get_now()
        for item in data['items']:
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat()
            }
        data['tender']['tenderPeriod'].update(
            {
                "startDate": (get_now() + timedelta(days=7)).isoformat()
            }
        )

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/relocation/tutorial/create-plan.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/plans?opt_pretty=1', {"data": data})
            self.assertEqual(response.status, '201 Created')

        plan = response.json['data']
        plan_id = plan['id']
        access = response.json['access']
        owner_token = access['token']
        orig_plan_transfer_token = access['transfer']

        self.app.authorization = ('Basic', ('broker2', ''))

        response = self.app.post_json('/transfers', {"data": {}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        transfer = response.json['data']
        access = response.json['access']
        new_access_token = access['token']
        new_transfer_token = access['transfer']

        with open('docs/source/relocation/tutorial/change-plan-ownership-forbidden.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/plans/{}/ownership'.format(plan_id),
                {"data": {"id": transfer['id'], 'transfer': orig_plan_transfer_token}}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(
                response.json['errors'][0]['description'],
                'Broker Accreditation level does not permit ownership change'
            )

        self.app.authorization = ('Basic', ('broker1', ''))

        with open('docs/source/relocation/tutorial/create-plan-transfer.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/transfers', {"data": {}})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            transfer = response.json['data']
            access = response.json['access']
            new_access_token = access['token']
            new_transfer_token = access['transfer']

        with open('docs/source/relocation/tutorial/get-plan-transfer.http', 'w') as self.app.file_obj:
            response = self.app.get('/transfers/{}'.format(transfer['id']))

        with open('docs/source/relocation/tutorial/change-plan-ownership.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/plans/{}/ownership'.format(plan_id),
                {"data": {"id": transfer['id'], 'transfer': orig_plan_transfer_token}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertNotIn('transfer', response.json['data'])
            self.assertNotIn('transfer_token', response.json['data'])
            self.assertEqual('broker1', response.json['data']['owner'])

        with open('docs/source/relocation/tutorial/get-used-plan-transfer.http', 'w') as self.app.file_obj:
            response = self.app.get('/transfers/{}'.format(transfer['id']))

        with open('docs/source/relocation/tutorial/modify-plan.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan_id, new_access_token),
                {"data": {"budget": {"description": "broker1 now can change the plan"}}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['budget']['description'], 'broker1 now can change the plan')

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json('/transfers', {"data": {}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        transfer = response.json['data']
        access = response.json['access']
        new_access_token = access['token']
        new_transfer_token = access['transfer']

        with open(
            'docs/source/relocation/tutorial/change-plan-ownership-forbidden-owner.http', 'w'
            ) as self.app.file_obj:
            response = self.app.post_json(
                '/plans/{}/ownership'.format(plan_id),
                {"data": {"id": transfer['id'], 'transfer': orig_plan_transfer_token}}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(
                response.json['errors'][0]['description'],
                'Owner Accreditation level does not permit ownership change'
            )

    def test_agreements_docs(self):
        test_tender_token = uuid4().hex
        data = deepcopy(test_agreement_data)
        data.update(
            {
                "dateSigned": get_now().isoformat(),
                "id": uuid4().hex,
                "tender_id": uuid4().hex,
                "tender_token": sha512(test_tender_token.encode()).hexdigest()
            }
        )
        tender_token = data['tender_token']
        self.app.authorization = ('Basic', ('agreements', ''))

        response = self.app.post_json('/agreements', {'data': data})
        self.assertEqual(response.status, '201 Created')
        agreement = response.json['data']
        self.assertEqual('broker', agreement['owner'])
        agreement_id = agreement['id']

        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/relocation/tutorial/get-agreement-credentials.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/agreements/{}/credentials?acc_token={}'.format(agreement_id, tender_token),
                {'data': ''}
            )
            self.assertEqual(response.status, '200 OK')
            access = response.json['access']
            token = access['token']
            agreement_transfer = access['transfer']

        self.app.authorization = ('Basic', ('broker2', ''))

        response = self.app.post_json('/transfers', {"data": {}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        transfer = response.json['data']
        access = response.json['access']
        new_access_token = access['token']
        new_transfer_token = access['transfer']

        with open(
            'docs/source/relocation/tutorial/change-agreement-ownership-forbidden.http', 'w'
            ) as self.app.file_obj:
            response = self.app.post_json(
                '/agreements/{}/ownership'.format(agreement_id),
                {"data": {"id": transfer['id'], 'transfer': agreement_transfer}}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(
                response.json['errors'][0]['description'],
                'Broker Accreditation level does not permit ownership change'
            )

        self.app.authorization = ('Basic', ('broker3', ''))
        with open('docs/source/relocation/tutorial/create-agreement-transfer.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/transfers', {"data": {}})
            self.assertEqual(response.status, '201 Created')
            transfer = response.json['data']
            self.assertIn('date', transfer)
            transfer_creation_date = transfer['date']
            access = response.json['access']
            new_access_token = access['token']
            new_transfer_token = access['transfer']

        with open('docs/source/relocation/tutorial/change-agreement-ownership.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/agreements/{}/ownership'.format(agreement_id),
                {"data": {"id": transfer['id'], 'transfer': agreement_transfer}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertNotIn('transfer', response.json['data'])
            self.assertNotIn('transfer_token', response.json['data'])
            self.assertEqual('broker3', response.json['data']['owner'])

        with open('docs/source/relocation/tutorial/modify-agreement.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/agreements/{}?acc_token={}'.format(agreement_id, new_access_token),
                {"data": {"terminationDetails": "broker3 now can change the contract"}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['terminationDetails'], 'broker3 now can change the contract')

        with open('docs/source/relocation/tutorial/get-used-agreement-transfer.http', 'w') as self.app.file_obj:
            response = self.app.get('/transfers/{}'.format(transfer['id']))

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json('/transfers', {"data": {}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        transfer = response.json['data']
        access = response.json['access']
        new_access_token = access['token']
        new_transfer_token = access['transfer']

        with open(
            'docs/source/relocation/tutorial/change-agreement-ownership-forbidden-owner.http', 'w'
            ) as self.app.file_obj:
            response = self.app.post_json(
                '/agreements/{}/ownership'.format(agreement_id),
                {"data": {"id": transfer['id'], 'transfer': agreement_transfer}}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(
                response.json['errors'][0]['description'],
                'Owner Accreditation level does not permit ownership change'
            )
