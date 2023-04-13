# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.question_blanks import (
    patch_tender_question,
    create_tender_question,
    lot_patch_tender_question_lots_none,
)
from openprocurement.tender.cfaua.tests.question_blanks import (
    lot_create_tender_question,
    lot_patch_tender_question,
    lot_create_tender_cancellations_and_questions,
)

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_author
from openprocurement.tender.belowthreshold.tests.question import TenderQuestionResourceTestMixin

from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_tender_cfaua_bids,
    test_tender_cfaua_lots,
)
from openprocurement.tender.openeu.tests.question_blanks import answering_question


class TenderQuestionResourceTest(BaseTenderContentWebTest, TenderQuestionResourceTestMixin):

    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_cfaua_bids
    author_data = test_tender_below_author

    test_create_tender_question = snitch(create_tender_question)
    test_patch_tender_question = snitch(patch_tender_question)
    test_answering_question = snitch(answering_question)


class TenderLotQuestionResourceTest(BaseTenderContentWebTest):
    initial_lots = test_tender_cfaua_lots
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_cfaua_bids
    author_data = test_tender_below_author

    test_create_tender_question = snitch(lot_create_tender_question)
    test_patch_tender_question = snitch(lot_patch_tender_question)
    test_lot_create_tender_cancellations_and_questions = snitch(lot_create_tender_cancellations_and_questions)
    test_lot_patch_tender_question_lots_none = snitch(lot_patch_tender_question_lots_none)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotQuestionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
