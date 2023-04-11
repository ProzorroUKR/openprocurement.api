# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_lots,
    test_tender_below_author,
)
from openprocurement.tender.belowthreshold.tests.question_blanks import (
    create_tender_question_invalid,
    create_tender_question,
    patch_tender_question,
    get_tender_question,
    get_tender_questions,
    lot_create_tender_question,
    lot_patch_tender_question,
    lot_patch_tender_question_lots_none,
    lot_patch_tender_question_items_none,
)


class TenderQuestionResourceTestMixin(object):
    test_create_tender_question_invalid = snitch(create_tender_question_invalid)
    test_get_tender_question = snitch(get_tender_question)
    test_get_tender_questions = snitch(get_tender_questions)


class TenderQuestionResourceTest(TenderContentWebTest, TenderQuestionResourceTestMixin):

    test_create_tender_question = snitch(create_tender_question)
    test_patch_tender_question = snitch(patch_tender_question)


class TenderLotQuestionResourceTest(TenderContentWebTest):
    initial_lots = 2 * test_tender_below_lots
    author_data = test_tender_below_author

    test_lot_create_tender_question = snitch(lot_create_tender_question)
    test_lot_patch_tender_question = snitch(lot_patch_tender_question)
    test_lot_patch_tender_question_lots_none = snitch(lot_patch_tender_question_lots_none)
    test_lot_patch_tender_question_items_none = snitch(lot_patch_tender_question_items_none)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotQuestionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
