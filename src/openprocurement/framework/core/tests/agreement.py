import datetime
import os
import unittest

from copy import deepcopy
from mock import MagicMock, patch
from openprocurement.api.constants import VERSION
from openprocurement.framework.core.utils import IsAgreement
from openprocurement.framework.core.tests.base import BaseAgreementTest
from openprocurement.framework.core.traversal import agreement_factory
from openprocurement.framework.core.utils import (
    agreement_from_data,
    agreement_serialize,
    register_agreement_agreementType,
    save_agreement,
    apply_patch,
    set_agreement_ownership,
)
from openprocurement.framework.core.models import (
    Agreement,
    get_agreement,
)
from openprocurement.framework.core.validation import validate_agreement_data
from openprocurement.framework.core.views.agreement import AgreementResource
from schematics.types import StringType


TEST_AGREEMENT = {
    "agreementID": "UA-2018-07-30-000001-afe4b1ed046845bcae5d675b0b8ca5aa1",
    "agreementType": "cfaua",
}


class AgreementsResourceTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    def test_empty_listing(self):
        response = self.app.get("/agreements")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], [])
        self.assertNotIn('{\n    "', response.body.decode())
        self.assertNotIn("callback({", response.body.decode())
        self.assertEqual(response.json["next_page"]["offset"], "")
        self.assertNotIn("prev_page", response.json)

        response = self.app.get("/agreements?opt_jsonp=callback")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/javascript")
        self.assertNotIn('{\n    "', response.body.decode())
        self.assertIn("callback({", response.body.decode())

        response = self.app.get("/agreements?opt_pretty=1")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn('{\n    "', response.body.decode())
        self.assertNotIn("callback({", response.body.decode())

        response = self.app.get("/agreements?opt_jsonp=callback&opt_pretty=1")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/javascript")
        self.assertIn('{\n    "', response.body.decode())
        self.assertIn("callback({", response.body.decode())

        offset = datetime.datetime.fromisoformat("2015-01-01T00:00:00+02:00").timestamp()
        response = self.app.get(f"/agreements?offset={offset}&descending=1&limit=10")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], [])
        self.assertIn("descending=1", response.json["next_page"]["uri"])
        self.assertIn("limit=10", response.json["next_page"]["uri"])
        self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
        self.assertIn("limit=10", response.json["prev_page"]["uri"])

        response = self.app.get("/agreements?offset=latest", status=404)
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{"description": "Invalid offset provided: latest",
              "location": "querystring", "name": "offset"}],
        )

        response = self.app.get("/agreements?descending=1&limit=10")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], [])
        self.assertIn("descending=1", response.json["next_page"]["uri"])
        self.assertIn("limit=10", response.json["next_page"]["uri"])
        self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
        self.assertIn("limit=10", response.json["prev_page"]["uri"])


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
        request.registry.agreement_agreementTypes.get.side_effect = [Agreement, None]
        model = agreement_from_data(request, TEST_AGREEMENT)
        self.assertTrue(model.agreementID)
        self.assertEqual(model.agreementID, TEST_AGREEMENT["agreementID"])
        with self.assertRaises(Exception) as e:
            res = agreement_from_data(request, TEST_AGREEMENT)

    def test_register_agreement_agreementType(self):
        config = MagicMock()
        model = MagicMock()
        agreementType = StringType(default="cfaua")
        model.agreementType = agreementType
        register_agreement_agreementType(config, model)

    def test_save_agreement(self):
        request = MagicMock(authenticated_userid="user_id")
        agreement = MagicMock()
        agreement.mode = "test"
        agreement.revisions = []
        agreement.dateModified = datetime.datetime(2018, 8, 2, 12, 9, 2, 440566)
        agreement.rev = "12341234"
        request.validated = {"agreement": agreement, "agreement_src": "src_test"}
        res = save_agreement(request)
        self.assertTrue(res)

    @patch("openprocurement.framework.core.utils.apply_data_patch")
    @patch("openprocurement.framework.core.utils.save_agreement")
    def test_apply_patch(self, mocked_apply_data_patch, mocked_save_agreement):
        request = MagicMock()
        agreement = MagicMock()
        agreement.__class__ = Agreement
        data = deepcopy(TEST_AGREEMENT)
        request.validated = {"data": data,
                             "agreement": agreement}
        mocked_save_agreement.return_value = True

        request.context.serialize.return_value = data
        res = apply_patch(request, "agreement")
        self.assertTrue(res)

        mocked_apply_data_patch.return_value = data
        res = apply_patch(request, "agreement")
        self.assertEqual(res, data)

    def test_set_agreement_ownership(self):
        item = MagicMock()
        request = MagicMock()
        set_agreement_ownership(item, request)

    def test_get_agreement(self):
        agreement = Agreement()
        dummy_object = MagicMock()
        dummy_object.__parent__ = agreement
        result = get_agreement(dummy_object)

        self.assertEqual(result, agreement)


class ValidationAgreementTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    @patch("openprocurement.framework.core.validation.validate_json_data")
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

    @patch("openprocurement.framework.core.views.agreement.save_agreement")
    def test_view(self, mocked_save_agreement):
        request = MagicMock()
        context = MagicMock()
        data = deepcopy(TEST_AGREEMENT)
        agreement = MagicMock()
        agreement.id = data["agreementID"]
        agreement.agreementID = data["agreementID"]
        agreement.agreementType = "cfaua"
        agreement.serialize.side_effect = [data]
        request.validated = {"agreement": agreement}
        mocked_save_agreement.side_effect = [True]
        view = AgreementResource(request=request, context=context)
        res = view.post()
        self.assertTrue(res["access"]["token"])
        self.assertEqual(res["data"], data)


class ModelAgreementTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    def test_agreement_model(self):
        data = deepcopy(TEST_AGREEMENT)
        agreement = Agreement()
        data["tender_id"] = "9a750db83cc64b34a879221513c13805"
        data["title"] = "test_name"
        data["description"] = "test description"
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

    @patch("openprocurement.framework.core.traversal.get_item")
    def test_factory(self, mocked_get_item):
        data = deepcopy(TEST_AGREEMENT)
        agreement = MagicMock()
        agreement.id = data["agreementID"]
        agreement.title = "test_factory"

        request = MagicMock()
        request.url = "http://localhost/api/" + VERSION + "/agreements"
        request.matchdict = {"agreement_id": data["agreementID"], "document_id": "9a750db83cc64b34a879221513c13805"}
        request.agreement = agreement
        request.method = "POST"
        mocked_get_item.side_effect = ["test_item1", "test_item2"]
        res = agreement_factory(request)
        self.assertEqual(res, "test_item1")
        self.assertEqual(mocked_get_item.called, True)
        request.matchdict = {"agreement_id": data["agreementID"], "contract_id": "9a750db83cc64b34a879221513c13805"}
        res = agreement_factory(request)
        self.assertEqual(res, "test_item2")
        self.assertEqual(mocked_get_item.called, True)
        request.matchdict = {"agreement_id": data["agreementID"]}
        res = agreement_factory(request)
        self.assertEqual(res.id, data["agreementID"])
        self.assertEqual(res.title, "test_factory")


class ResourcesAgreementTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    def test_IsAgreement(self):
        config = MagicMock()
        request = MagicMock()
        context = MagicMock()
        obj = IsAgreement(val="cfa-ua_test", config=config)
        agreement_type = obj.text()
        self.assertEqual(agreement_type, "agreementType = cfa-ua_test")
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


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
