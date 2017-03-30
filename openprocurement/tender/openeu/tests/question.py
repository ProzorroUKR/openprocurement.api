# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_bids,
    test_lots,
)
from openprocurement.tender.openeu.tests.questions_blanks import (
    # TenderLotQuestionResourceTest
    lot_create_tender_question,
    lot_patch_tender_question,
    # TenderQuestionResourceTest
    create_tender_question_invalid,
    create_tender_question,
    patch_tender_question,
    get_tender_question,
    get_tender_questions,
)


class TenderQuestionResourceTest(BaseTenderContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids

    test_create_tender_question_invalid = snitch(create_tender_question_invalid)
    test_create_tender_question = snitch(create_tender_question)
    test_patch_tender_question = snitch(patch_tender_question)
    test_get_tender_question = snitch(get_tender_question)
    test_get_tender_questions = snitch(get_tender_questions)


class TenderLotQuestionResourceTest(BaseTenderContentWebTest):

    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids

    test_create_tender_question = snitch(lot_create_tender_question)
    test_patch_tender_question = snitch(lot_patch_tender_question)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
