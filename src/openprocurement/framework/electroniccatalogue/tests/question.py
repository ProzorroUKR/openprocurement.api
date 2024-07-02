import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.framework.dps.tests.question_blanks import (
    create_question_check_enquiry_period,
    create_question_check_framework_status,
    create_question_invalid,
    get_framework_question,
    get_framework_questions,
    patch_framework_question,
)
from openprocurement.framework.electroniccatalogue.tests.base import (
    FrameworkContentWebTest,
    test_framework_electronic_catalogue_config,
    test_framework_electronic_catalogue_data,
)


class QuestionResourceTest(FrameworkContentWebTest):
    initial_data = test_framework_electronic_catalogue_data
    initial_config = test_framework_electronic_catalogue_config
    initial_auth = ("Basic", ("broker", ""))

    test_create_question_invalid = snitch(create_question_invalid)
    test_create_question_check_framework_status = snitch(create_question_check_framework_status)
    test_create_question_check_enquiry_period = snitch(create_question_check_enquiry_period)
    test_patch_framework_question = snitch(patch_framework_question)
    test_get_framework_question = snitch(get_framework_question)
    test_get_framework_questions = snitch(get_framework_questions)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(QuestionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
