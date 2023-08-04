import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.framework.electroniccatalogue.tests.base import (
    test_framework_electronic_catalogue_data,
    FrameworkContentWebTest,
)
from openprocurement.framework.dps.tests.question_blanks import (
    create_question_invalid,
    create_question_check_framework_status,
    create_question_check_enquiry_period,
    patch_framework_question,
    get_framework_question,
    get_framework_questions,
)


class QuestionResourceTest(FrameworkContentWebTest):
    initial_data = test_framework_electronic_catalogue_data
    initial_auth = ("Basic", ("broker", ""))

    test_create_question_invalid = snitch(create_question_invalid)
    test_create_question_check_framework_status = snitch(create_question_check_framework_status)
    test_create_question_check_enquiry_period = snitch(create_question_check_enquiry_period)
    test_patch_framework_question = snitch(patch_framework_question)
    test_get_framework_question = snitch(get_framework_question)
    test_get_framework_questions = snitch(get_framework_questions)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QuestionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
