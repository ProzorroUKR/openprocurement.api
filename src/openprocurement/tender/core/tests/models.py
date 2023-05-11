# # -*- coding: utf-8 -*-
# TODO: Rewrite for new models
# import copy
# import unittest
# from mock import patch, MagicMock
# from datetime import datetime, timedelta
# from schematics.exceptions import ModelValidationError
# from schematics.types.compound import ModelType
# from openprocurement.tender.core.models import (
#     PeriodEndRequired,
#     get_tender,
#     Tender,
#     Question,
#     ProcuringEntity,
# )
# from openprocurement.api.constants import TZ
# import pytest
#
#
# class TestPeriodEndRequired(unittest.TestCase):
#     @patch("openprocurement.tender.core.models.get_tender")
#     def test_validate_start_date(self, mocked_get_tender):
#         start_date = datetime.now(TZ)
#         end_date = datetime.now(TZ) + timedelta(minutes=3)
#         model = PeriodEndRequired({"startDate": end_date.isoformat(), "endDate": start_date.isoformat()})
#         with self.assertRaises(ModelValidationError) as e:
#             model.validate()
#         self.assertEqual(e.exception.messages, {"startDate": ["period should begin before its end"]})
#
#         mocked_get_tender.return_value = {"revisions": [{"date": datetime.now(TZ).isoformat()}]}
#         model = PeriodEndRequired({"endDate": end_date.isoformat()})
#         with self.assertRaises(ModelValidationError) as e:
#             model.validate()
#         self.assertEqual(e.exception.messages, {"startDate": ["This field cannot be deleted"]})
#
#         model = PeriodEndRequired({"startDate": start_date.isoformat(), "endDate": end_date.isoformat()})
#         model.validate()
#         self.assertEqual(start_date, model.startDate)
#         self.assertEqual(end_date, model.endDate)
#
#
# class TestModelsUtils(unittest.TestCase):
#     def test_get_tender(self):
#         period = PeriodEndRequired({"startDate": datetime.now(TZ).isoformat(), "endDate": datetime.now(TZ).isoformat()})
#         second_period = PeriodEndRequired(
#             {"startDate": datetime.now(TZ).isoformat(), "endDate": datetime.now(TZ).isoformat()}
#         )
#         tender = Tender()
#         period._data["__parent__"] = tender
#         second_period._data["__parent__"] = period
#
#         parent_tender = get_tender(second_period)
#         self.assertEqual(tender, parent_tender)
#         self.assertIsInstance(parent_tender, Tender)
#         self.assertIsInstance(tender, Tender)
#
#         period._data["__parent__"] = None
#         with self.assertRaises(AttributeError) as e:
#             get_tender(second_period)
#         self.assertEqual(str(e.exception), "'NoneType' object has no attribute '__parent__'")
#
#
# class TestQuestionModel(unittest.TestCase):
#     def test_serialize_pre_qualification(self):
#         question = Question()
#         with self.assertRaises(ValueError) as e:
#             question.serialize("invalid_role")
#         self.assertIsInstance(e.exception, ValueError)
#         self.assertEqual(str(e.exception), 'Question Model has no role "invalid_role"')
#         serialized_question = question.serialize("active.pre-qualification")
#         self.assertEqual(serialized_question["questionOf"], "tender")
#         self.assertEqual(len(serialized_question["id"]), 32)
#
#         serialized_question = question.serialize("active.pre-qualification.stand-still")
#         self.assertEqual(serialized_question["questionOf"], "tender")
#         self.assertEqual(len(serialized_question["id"]), 32)
#
#
# class TestTenderMainProcurementCategory(unittest.TestCase):
#     milestones = {
#         "id": "a" * 32,
#         "title": "signingTheContract",
#         "code": "prepayment",
#         "type": "financing",
#         "duration": {"days": 2, "type": "banking"},
#         "sequenceNumber": 0,
#         "percentage": 100,
#     }
#
#     def test_validate_valid(self):
#         tender = Tender(
#             {"title": "whatever", "mainProcurementCategory": "goods", "milestones": [copy.deepcopy(self.milestones)]}
#         )
#         tender.validate()
#         data = tender.serialize("embedded")
#         self.assertIn("mainProcurementCategory", data)
#         self.assertIn(data["mainProcurementCategory"], "goods")
#
#     def test_validate_not_valid(self):
#         tender = Tender(
#             {"title": "whatever", "mainProcurementCategory": "test", "milestones": [copy.deepcopy(self.milestones)]}
#         )
#         with self.assertRaises(ModelValidationError) as e:
#             tender.validate()
#         self.assertEqual(
#             e.exception.messages, {"mainProcurementCategory": ["Value must be one of ['goods', 'services', 'works']."]}
#         )
#
#     def test_validate_empty(self):
#         with self.assertRaises(ModelValidationError) as e:
#             tender = Tender({"title": "whatever", "milestones": [copy.deepcopy(self.milestones)]})
#             tender.validate()
#         self.assertEqual(e.exception.messages, {"mainProcurementCategory": ["This field is required."]})
#
#
# class TestTender(Tender):
#     procuringEntity = ModelType(ProcuringEntity, required=True)
#
#     def validate_mainProcurementCategory(self, *_):
#         pass
#
#     def validate_milestones(self, *_):
#         pass
#
#     def validate_buyers(self, *_):
#         pass
#
#
# @pytest.mark.parametrize(
#     "test_data",
#     [
#         ([], "general", True),
#         ([], None, True),
#         ([], "central", True),
#         ([{"id": "a" * 32}], "general", True),
#         ([{"id": "a" * 32}], None, True),
#         ([{"id": "a" * 32}], "central", True),
#         ([{"id": "a" * 32}, {"id": "b" * 32}], "general", False),
#         ([{"id": "a" * 32}, {"id": "b" * 32}], None, False),
#         ([{"id": "a" * 32}, {"id": "b" * 32}], "central", True),
#     ],
# )
# def test_plans_and_kind_validation(test_data):
#     plans, kind, result = test_data
#     tender = TestTender(
#         {
#             "title": "whatever",
#             "procuringEntity": {
#                 "name": "Державне управління справами",
#                 "identifier": {"scheme": "UA-EDR", "id": "00037256", "uri": "http://www.dus.gov.ua/"},
#                 "address": {"countryName": "Україна"},
#                 "contactPoint": {"name": "Державне управління справами", "telephone": "+0440000000"},
#                 "kind": kind,
#             },
#             "plans": plans,
#         }
#     )
#     try:
#         tender.validate()
#     except ModelValidationError as e:
#         assert result is False, "No exceptions were expected"
#         assert e.args == (
#             {"plans": ["Linking more than one plan is allowed only if procuringEntity.kind is 'central'"]},
#         )
#     else:
#         assert result is True, "ModelValidationError was expected"
#
# def suite():
#     suite = unittest.TestSuite()
#     suite.addTest(unittest.makeSuite(TestPeriodEndRequired))
#     suite.addTest(unittest.makeSuite(TestModelsUtils))
#     return suite
#
#
# if __name__ == "__main__":
#     unittest.main(defaultTest="suite")
