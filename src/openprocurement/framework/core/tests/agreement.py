import datetime
import os
import unittest

from copy import deepcopy
from mock import MagicMock, patch
from openprocurement.framework.core.utils import AgreementTypePredicate
from openprocurement.framework.core.tests.base import BaseAgreementTest
from openprocurement.framework.core.utils import (
    register_agreement_agreementType,
)
from openprocurement.framework.core.validation import validate_agreement_data
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

    def test_register_agreement_agreementType(self):
        config = MagicMock()
        model = MagicMock()
        agreementType = StringType(default="cfaua")
        model.agreementType = agreementType
        register_agreement_agreementType(config, model)



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


class ResourcesAgreementTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    def test_IsAgreement(self):
        config = MagicMock()
        request = MagicMock()
        context = MagicMock()
        obj = AgreementTypePredicate(val="cfa-ua_test", config=config)
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
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
