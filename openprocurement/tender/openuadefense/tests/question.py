# -*- coding: utf-8 -*-
import unittest
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.openuadefense.tests.base import BaseTenderUAContentWebTest
from openprocurement.tender.openuadefense.tests.question_blanks import (
    create_tender_question_invalid,
    create_tender_question,
    patch_tender_question,
    get_tender_question,
    get_tender_questions,
    create_multilot_tender_question,
    patch_multilot_tender_question,
)


class TenderQuestionResourceTest(BaseTenderUAContentWebTest):

    test_create_tender_question_invalid = snitch(create_tender_question_invalid)

    test_create_tender_question = snitch(create_tender_question)

    test_patch_tender_question = snitch(patch_tender_question)

    test_get_tender_question = snitch(get_tender_question)

    test_get_tender_questions = snitch(get_tender_questions)


class TenderLotQuestionResourceTest(BaseTenderUAContentWebTest):

    initial_lots = 2 * test_lots

    test_create_tender_question = snitch(create_multilot_tender_question)

    test_patch_tender_question = snitch(patch_multilot_tender_question)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
