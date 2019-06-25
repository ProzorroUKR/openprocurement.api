import datetime
import os
import unittest

from copy import deepcopy
from mock import MagicMock, patch
from openprocurement.api.constants import VERSION
from openprocurement.agreement.core.resource import IsAgreement
from openprocurement.agreement.core.tests.base import BaseAgreementTest, TEST_AGREEMENT
from openprocurement.agreement.core.traversal import factory
from openprocurement.agreement.core.utils import (
    agreement_from_data,
    agreement_serialize,
    extract_agreement_by_id,
    register_agreement_type,
    save_agreement,
    apply_patch, set_ownership, extract_agreement,
    get_agreement)
from openprocurement.agreement.core.models.agreement import Agreement
from openprocurement.agreement.core.validation import validate_agreement_data
from openprocurement.agreement.core.views.agreement import APIAgreementsResource
from schematics.types import StringType


class AgreementsResourceTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    def test_empty_listing(self):
        response = self.app.get('/agreements')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertNotIn('{\n    "', response.body)
        self.assertNotIn('callback({', response.body)
        self.assertEqual(response.json['next_page']['offset'], '')
        self.assertNotIn('prev_page', response.json)

        response = self.app.get('/agreements?opt_jsonp=callback')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertNotIn('{\n    "', response.body)
        self.assertIn('callback({', response.body)

        response = self.app.get('/agreements?opt_pretty=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "', response.body)
        self.assertNotIn('callback({', response.body)

        response = self.app.get('/agreements?opt_jsonp=callback&opt_pretty=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('{\n    "', response.body)
        self.assertIn('callback({', response.body)

        response = self.app.get('/agreements?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertIn('descending=1', response.json['next_page']['uri'])
        self.assertIn('limit=10', response.json['next_page']['uri'])
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertIn('limit=10', response.json['prev_page']['uri'])

        response = self.app.get('/agreements?feed=changes')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertEqual(response.json['next_page']['offset'], '')
        self.assertNotIn('prev_page', response.json)

        response = self.app.get('/agreements?feed=changes&offset=0', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Offset expired/invalid', u'location': u'params', u'name': u'offset'}
        ])

        response = self.app.get('/agreements?feed=changes&descending=1&limit=10')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertIn('descending=1', response.json['next_page']['uri'])
        self.assertIn('limit=10', response.json['next_page']['uri'])
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertIn('limit=10', response.json['prev_page']['uri'])


class UtilsAgreementTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    def test_agreement_serialize(self):
        request = MagicMock()
        agreement_data = deepcopy(TEST_AGREEMENT)
        fields = []
        res = agreement_serialize(request, agreement_data, fields)
        self.assertEqual(res, {})

    def test_agreement_from_data(self):
        request = MagicMock()
        request.registry.agreements_types.get.side_effect = [Agreement, None]
        model = agreement_from_data(request, TEST_AGREEMENT)
        self.assertTrue(model.id)
        self.assertTrue(model.agreementID)
        self.assertEqual(model.agreementID, TEST_AGREEMENT['agreementID'])
        with self.assertRaises(Exception) as e:
            res = agreement_from_data(request, TEST_AGREEMENT)

    @patch('openprocurement.agreement.core.utils.decode_path_info')
    def test_extract_agreement_by_id(self, mocked_decode_path_info):
        data = deepcopy(TEST_AGREEMENT)
        agreement_id = data['agreementID']
        request = MagicMock()
        request.agreement_from_data.return_value = True
        request.matchdict = {'agreement_id': data['agreementID']}
        request.registry.db = {data['agreementID']: {'doc_type': 'agreement'}}
        with self.assertRaises(Exception) as e:
            res = extract_agreement_by_id(request, agreement_id)
        request.registry.db = {data['agreementID']: {'doc_type': 'Test_agreement'}}
        with self.assertRaises(Exception) as e:
            res = extract_agreement_by_id(request, agreement_id)
        request.registry.db = {data['agreementID']: {'doc_type': 'Agreement'}}
        res = extract_agreement_by_id(request, agreement_id)
        self.assertEqual(res, True)
        mocked_decode_path_info.side_effect = [
            '/', '/url/test/agreements/{}'.format(data['agreementID'],
            KeyError('Missing \'PATH_INFO\''),
            UnicodeDecodeError('UTF-8', 'obj', 1, 10, 'Hm...'),)
        ]
        res = extract_agreement(request)
        self.assertFalse(res)
        res = extract_agreement(request)
        self.assertEqual(res, True)
        with self.assertRaises(Exception) as e:
            res = extract_agreement(request)
        with self.assertRaises(Exception) as e:
            res = extract_agreement(request)

    def test_register_agreement_type(self):
        config = MagicMock()
        model = MagicMock()
        agreementType = StringType(default='cfaua')
        model.agreementType = agreementType
        register_agreement_type(config, model)

    def test_save_agreement(self):
        request = MagicMock()
        agreement = MagicMock()
        agreement.mode = u'test'
        agreement.revisions = []
        agreement.dateModified = datetime.datetime(2018, 8, 2, 12, 9, 2, 440566)
        type(agreement).revisions = MagicMock()
        agreement.rev = '12341234'
        request.validated = {
            'agreement': agreement,
            'agreement_src': 'src_test'
        }
        res = save_agreement(request)
        self.assertTrue(res)

    @patch('openprocurement.agreement.core.utils.apply_data_patch')
    @patch('openprocurement.agreement.core.utils.save_agreement')
    def test_apply_patch(self, mocked_apply_data_patch, mocked_save_agreement):
        request = MagicMock()
        data = deepcopy(TEST_AGREEMENT)
        request.validated = {'data': data}
        mocked_save_agreement.return_value = True

        request.context.serialize.return_value = data
        res = apply_patch(request)
        self.assertTrue(res)

        mocked_apply_data_patch.return_value = data
        res = apply_patch(request)
        self.assertEqual(res, data)

    def test_set_ownership(self):
        item = MagicMock()
        request = MagicMock()
        set_ownership(item, request)

    def test_get_agreement(self):
        agreement = Agreement()
        dummy_object = MagicMock()
        dummy_object.__parent__ = agreement
        result = get_agreement(dummy_object)

        self.assertEqual(result, agreement)


class ValidationAgreementTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    @patch('openprocurement.agreement.core.validation.validate_json_data')
    def test_validate_agreement_data(self, mocked_validation_json_data):
        request = MagicMock()
        data = deepcopy(TEST_AGREEMENT)
        model = MagicMock()
        request.check_accreditations.side_effect = [False, True]
        mocked_validation_json_data.side_effect = [data, data]
        request.agreement_from_data.side_effect = [model, model]
        with self.assertRaises(Exception) as e:
            res = validate_agreement_data(request)
        res = validate_agreement_data(request)
        self.assertTrue(res)


class ViewsAgreementTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    @patch('openprocurement.agreement.core.views.agreement.save_agreement')
    def test_view(self, mocked_save_agreement):
        request = MagicMock()
        context = MagicMock()
        data = deepcopy(TEST_AGREEMENT)
        agreement = MagicMock()
        agreement.id = data['agreementID']
        agreement.agreementID = data['agreementID']
        agreement.agreementType = 'cfaua'
        agreement.serialize.side_effect = [data]
        request.validated = {'agreement': agreement}
        mocked_save_agreement.side_effect = [True]
        view = APIAgreementsResource(request=request, context=context)
        res = view.post()
        self.assertTrue(res['access']['token'])
        self.assertEqual(res['data'], data)


class ModelAgreementTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    def test_agreement_model(self):
        data = deepcopy(TEST_AGREEMENT)
        agreement = Agreement()
        data['tender_id'] = '9a750db83cc64b34a879221513c13805'
        data['title'] = 'test_name'
        data['description'] = 'test description'
        res = agreement.import_data(data)
        self.assertTrue(res)
        roles = agreement.__local_roles__()
        self.assertTrue(roles)
        acl = agreement.__acl__()
        self.assertTrue(acl)
        repr = agreement.__repr__()
        self.assertTrue(repr)


class TraversalAgreementTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    @patch('openprocurement.agreement.core.traversal.get_item')
    def test_factory(self, mocked_get_item):
        data = deepcopy(TEST_AGREEMENT)
        agreement = MagicMock()
        agreement.id = data['agreementID']
        agreement.title = 'test_factory'

        request = MagicMock()
        request.url = 'http://localhost/api/' + VERSION + '/agreements'
        request.matchdict = {'agreement_id': data['agreementID'],
                             'document_id': '9a750db83cc64b34a879221513c13805'}
        request.agreement = agreement
        request.method = 'POST'
        mocked_get_item.side_effect = ['test_item1', 'test_item2']
        res = factory(request)
        self.assertEqual(res, 'test_item1')
        self.assertEqual(mocked_get_item.called, True)
        request.matchdict = {'agreement_id': data['agreementID'],
                             'contract_id': '9a750db83cc64b34a879221513c13805'}
        res = factory(request)
        self.assertEqual(res, 'test_item2')
        self.assertEqual(mocked_get_item.called, True)
        request.matchdict = {'agreement_id': data['agreementID']}
        res = factory(request)
        self.assertEqual(res.id, data['agreementID'])
        self.assertEqual(res.title, 'test_factory')


class ResourcesAgreementTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    def test_IsAgreement(self):
        config = MagicMock()
        request = MagicMock()
        context = MagicMock()
        obj = IsAgreement(val='cfa-ua_test', config=config)
        agreement_type = obj.text()
        self.assertEqual(agreement_type, 'agreementType = cfa-ua_test')
        res_call = obj.__call__(context=context, request=request)
        self.assertFalse(res_call)
        request.agreement = None
        res_call = obj.__call__(context=context, request=request)
        self.assertFalse(res_call)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AgreementsResourceTest))
    suite.addTest(unittest.makeSuite(UtilsAgreementTest))
    suite.addTest(unittest.makeSuite(ValidationAgreementTest))
    suite.addTest(unittest.makeSuite(ViewsAgreementTest))
    suite.addTest(unittest.makeSuite(ModelAgreementTest))
    suite.addTest(unittest.makeSuite(TraversalAgreementTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
