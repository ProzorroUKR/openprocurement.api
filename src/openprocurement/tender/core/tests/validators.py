# TODO: Rewrite for new models
# import copy
# from datetime import timedelta
#
# import mock
# import unittest
# from decimal import Decimal
#
# from pyramid.httpexceptions import HTTPError
# from schematics.exceptions import ModelValidationError
#
# from openprocurement.api.utils import get_now
# from openprocurement.tender.core.validation import (
#     validate_update_contract_value_amount,
# )
# from openprocurement.tender.belowthreshold.models import Tender
# from openprocurement.tender.belowthreshold.tests.base import (
#     test_tender_below_data,
#     test_tender_below_lots,
# )
#
#
# def generate_contract_value_patch_request_mock(contract_value, award_value=None):
#     request = mock.MagicMock(validated={})
#     if award_value:
#         award = mock.MagicMock(id="test_award_id", value=mock.Mock(**award_value))
#         contract = mock.MagicMock(id="contract_id", awardID="test_award_id")
#         request.validated["tender"] = mock.MagicMock(awards=[award], contracts=[contract])
#         request.validated["id"] = 'contract_id'
#         request.context.awardID = "test_award_id"
#     request.validated["data"] = request.validated["json_data"] = {"value": contract_value}
#     return request
#
#
# @mock.patch("openprocurement.api.utils.error_handler", lambda *_: HTTPError)
# class TestValidateUpdateContractValueAmount(unittest.TestCase):
#     def test_amount_net_greater_than_amount_error(self):
#         request = generate_contract_value_patch_request_mock(
#             contract_value={"amount": 100, "amountNet": 200, "currency": "USD", "valueAddedTaxIncluded": True}
#         )
#
#         with self.assertRaises(HTTPError):
#             validate_update_contract_value_amount(request)
#
#         request.errors.add.assert_called_once_with(
#             "body", "value", "Amount should be equal or greater than amountNet and differ by no more than 20.0%"
#         )
#
#     def test_amount_net_too_match_less_than_amount_error(self):
#         request = generate_contract_value_patch_request_mock(
#             contract_value={"amount": 100, "amountNet": 50, "currency": "USD", "valueAddedTaxIncluded": True}
#         )
#
#         with self.assertRaises(HTTPError):
#             validate_update_contract_value_amount(request)
#
#         request.errors.add.assert_called_once_with(
#             "body", "value", "Amount should be equal or greater than amountNet and differ by no more than 20.0%"
#         )
#
#     def test_amount_net_not_equal_to_amount_error(self):
#         request = generate_contract_value_patch_request_mock(
#             contract_value={"amount": 100, "amountNet": 50, "currency": "USD", "valueAddedTaxIncluded": False}
#         )
#
#         with self.assertRaises(HTTPError):
#             validate_update_contract_value_amount(request)
#
#         request.errors.add.assert_called_once_with("body", "value", "Amount and amountNet should be equal")
#
#     def test_from_float(self):
#         amount = 1478.4
#         amount_net = 1232.0
#         coef = 1.2
#
#         #  the problem
#         assert amount_net * coef == 1478.3999999999999
#
#         request = generate_contract_value_patch_request_mock(
#             contract_value={"amount": amount, "amountNet": amount_net, "currency": "USD", "valueAddedTaxIncluded": True}
#         )
#
#         try:
#             validate_update_contract_value_amount(request)
#         except HTTPError:
#             self.fail("validate_update_contract_value_amount() raised HTTPError unexpectedly")
#
#     def test_from_decimal(self):
#         amount = Decimal("1478.4")
#         amount_net = Decimal("1232.0")
#         coef = Decimal("1.2")
#
#         request = generate_contract_value_patch_request_mock(
#             contract_value={"amount": amount, "amountNet": amount_net, "currency": "USD", "valueAddedTaxIncluded": True}
#         )
#
#         try:
#             validate_update_contract_value_amount(request)
#         except HTTPError:
#             self.fail("validate_update_contract_value_amount() raised HTTPError unexpectedly")
#
#     def test_round_up_from_float(self):
#         amount = 120.14
#         amount_net = 100.11
#         coef = 1.2
#
#         request = generate_contract_value_patch_request_mock(
#             contract_value={"amount": amount, "amountNet": amount_net, "currency": "USD", "valueAddedTaxIncluded": True}
#         )
#
#         try:
#             validate_update_contract_value_amount(request)
#         except HTTPError:
#             self.fail("validate_update_contract_value_amount() raised HTTPError unexpectedly")
#
#     def test_round_up_from_decimal(self):
#         amount = Decimal("120.14")
#         amount_net = Decimal("100.11")
#         coef = Decimal("1.2")
#
#         request = generate_contract_value_patch_request_mock(
#             contract_value={"amount": amount, "amountNet": amount_net, "currency": "USD", "valueAddedTaxIncluded": True}
#         )
#
#         try:
#             validate_update_contract_value_amount(request)
#         except HTTPError:
#             self.fail("validate_update_contract_value_amount() raised HTTPError unexpectedly")
#
#
# class TestTenderAdditionalClassificationUAROAD(unittest.TestCase):
#
#     valid_ua_road = {
#         "scheme": "UA-ROAD",
#         "id": "M-06",
#         "description": "Київ - Чоп (на м. Будапешт через мм. Львів, Мукачево і Ужгород)",
#     }
#
#     def setUp(self):
#         self.test_tender = copy.deepcopy(test_tender_below_data)
#
#     def test_with_invalid_cpv(self):
#         self.test_tender["items"][0]["additionalClassifications"].append(self.valid_ua_road)
#         tender = Tender(self.test_tender)
#         with self.assertRaises(ModelValidationError) as e:
#             tender.validate()
#         error_message = e.exception.messages["items"][0]["additionalClassifications"][0]
#         self.assertIn(
#             "Item shouldn't have additionalClassification with scheme UA-ROAD for cpv not starts with", error_message
#         )
#
#     def test_valid(self):
#         self.test_tender["items"][0]["classification"]["id"] = "71322200-3"
#         self.test_tender["items"][0]["additionalClassifications"].append(self.valid_ua_road)
#         tender = Tender(self.test_tender)
#         tender.validate()
#
#     def test_invalid_id(self):
#         self.test_tender["items"][0]["classification"]["id"] = "71322200-3"
#         self.test_tender["items"][0]["additionalClassifications"].append(
#             {
#                 "scheme": "UA-ROAD",
#                 "id": "some invalid id",
#                 "description": "Київ - Чоп (на м. Будапешт через мм. Львів, Мукачево і Ужгород)",
#             }
#         )
#         tender = Tender(self.test_tender)
#         with self.assertRaises(ModelValidationError) as e:
#             tender.validate()
#         error_message = e.exception.messages["items"][0]["additionalClassifications"][0]["id"][0]
#         self.assertEqual(error_message, "UA-ROAD id not found in standards")
#
#     def test_invalid_description(self):
#         self.test_tender["items"][0]["classification"]["id"] = "71322200-3"
#         self.test_tender["items"][0]["additionalClassifications"].append(
#             {"scheme": "UA-ROAD", "id": "М-06", "description": "Some invalid description"}
#         )
#         tender = Tender(self.test_tender)
#         with self.assertRaises(ModelValidationError) as e:
#             tender.validate()
#         error_message = e.exception.messages["items"][0]["additionalClassifications"][0]["description"][0]
#         self.assertEqual("UA-ROAD description invalid", error_message)
#
#     def test_more_than_one_ua_road(self):
#         self.test_tender["items"][0]["classification"]["id"] = "71322200-3"
#         self.test_tender["items"][0]["additionalClassifications"] = [self.valid_ua_road, self.valid_ua_road]
#         tender = Tender(self.test_tender)
#         with self.assertRaises(ModelValidationError) as e:
#             tender.validate()
#         error_message = e.exception.messages["items"][0]["additionalClassifications"][0]
#         self.assertIn("Item shouldn't have more than 1 additionalClassification", error_message)
#
#     def test_required_id_description(self):
#         self.test_tender["items"][0]["classification"]["id"] = "71322200-3"
#         self.test_tender["items"][0]["additionalClassifications"] = [{"scheme": "UA-ROAD"}]
#         tender = Tender(self.test_tender)
#         with self.assertRaises(ModelValidationError) as e:
#             tender.validate()
#         error_messages = e.exception.messages["items"][0]["additionalClassifications"][0]
#         self.assertEqual(
#             error_messages, {"id": ["This field is required."], "description": ["This field is required."]}
#         )
#
#
# class TestTenderAdditionalClassificationGMDN(unittest.TestCase):
#
#     valid_gmdn = {"scheme": "GMDN", "id": "10024", "description": "Адаптометр"}
#
#     def setUp(self):
#         self.test_tender = copy.deepcopy(test_tender_below_data)
#
#     def test_with_invalid_cpv(self):
#         self.test_tender["items"][0]["additionalClassifications"] = [self.valid_gmdn]
#         tender = Tender(self.test_tender)
#         with self.assertRaises(ModelValidationError) as e:
#             tender.validate()
#         error_message = e.exception.messages["items"][0]["additionalClassifications"][0]
#         self.assertIn(
#             "Item shouldn't have additionalClassification with scheme GMDN for cpv not starts with", error_message
#         )
#
#     def test_valid(self):
#         self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
#         self.test_tender["items"][0]["additionalClassifications"] = [self.valid_gmdn]
#         tender = Tender(self.test_tender)
#         tender.validate()
#
#     def test_invalid_id(self):
#         self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
#         self.test_tender["items"][0]["additionalClassifications"] = [
#             {"scheme": "GMDN", "id": "some invalid id", "description": "Адаптометр"}
#         ]
#         tender = Tender(self.test_tender)
#         with self.assertRaises(ModelValidationError) as e:
#             tender.validate()
#         error_message = e.exception.messages["items"][0]["additionalClassifications"][0]["id"][0]
#         self.assertEqual(error_message, "GMDN id not found in standards")
#
#     def test_invalid_description(self):
#         self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
#         self.test_tender["items"][0]["additionalClassifications"] = [
#             {"scheme": "GMDN", "id": "10024", "description": "Адаптометр invalid"}
#         ]
#         tender = Tender(self.test_tender)
#         tender.validate()  # description isn't validated
#
#     def test_more_than_one_gmdn(self):
#         self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
#         self.test_tender["items"][0]["additionalClassifications"] = [self.valid_gmdn, self.valid_gmdn]
#         tender = Tender(self.test_tender)
#         with self.assertRaises(ModelValidationError) as e:
#             tender.validate()
#         error_message = e.exception.messages["items"][0]["additionalClassifications"][0]
#         self.assertIn("Item shouldn't have more than 1 additionalClassification", error_message)
#
#     def test_gmdn_with_inn_atc(self):
#         self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
#         for scheme in ["INN", "ATC"]:
#             self.test_tender["items"][0]["additionalClassifications"] = [
#                 self.valid_gmdn,
#                 {"scheme": scheme, "id": "id", "description": "description"},
#             ]
#             tender = Tender(self.test_tender)
#             with self.assertRaises(ModelValidationError) as e:
#                 tender.validate()
#             error_message = e.exception.messages["items"][0]["additionalClassifications"][0]
#             self.assertIn(
#                 "Item shouldn't have additionalClassifications with both schemes INN/ATC and GMDN", error_message
#             )
#
#     def test_required_id_description(self):
#         self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
#         self.test_tender["items"][0]["additionalClassifications"] = [{"scheme": "GMDN"}]
#         tender = Tender(self.test_tender)
#         with self.assertRaises(ModelValidationError) as e:
#             tender.validate()
#         error_messages = e.exception.messages["items"][0]["additionalClassifications"][0]
#         self.assertEqual(
#             error_messages, {"id": ["This field is required."], "description": ["This field is required."]}
#         )
#
#
# class TestTenderMinimalStepLimitsValidation(unittest.TestCase):
#
#     def setUp(self):
#         self.test_tender = copy.deepcopy(test_tender_below_data)
#         self.test_lots = copy.deepcopy(test_tender_below_lots)
#
#     @mock.patch("openprocurement.tender.core.validation.MINIMAL_STEP_VALIDATION_FROM", get_now() - timedelta(days=1))
#     def test_validate_tender_minimalstep(self):
#         self.test_tender["minimalStep"]["amount"] = 35
#         tender = Tender(self.test_tender)
#         with self.assertRaises(ModelValidationError) as e:
#             tender.validate()
#         self.assertEqual(
#             e.exception.messages,
#             {'minimalStep': ['minimalstep must be between 0.5% and 3% of value (with 2 digits precision).']}
#         )
#
#     @mock.patch("openprocurement.tender.core.validation.MINIMAL_STEP_VALIDATION_FROM", get_now() + timedelta(days=1))
#     def test_not_validate_tender_minimalstep_before_feature_start_date(self):
#         self.test_tender["minimalStep"]["amount"] = 35
#         tender = Tender(self.test_tender)
#         tender.validate()
#
#     def test_not_validate_minimalstep_for_tender_with_lots(self):
#         self.test_tender["minimalStep"]["amount"] = 35
#         self.test_tender["lots"] = self.test_lots
#         tender = Tender(self.test_tender)
#         tender.validate()
