# -*- coding: utf-8 -*-
import unittest
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.question import TenderQuestionResourceTestMixin
from openprocurement.tender.belowthreshold.tests.question_blanks import (
    # CompetitiveDialogQuestionResourceTest
    patch_tender_question,
    # CompetitiveDialogQLotQuestionResourceTest
    lot_create_tender_question,
    lot_patch_tender_question,
)

from openprocurement.tender.openua.tests.question_blanks import (
    # TenderQuestionResourceTest
    create_tender_question as create_tender_question_ua,
)

from openprocurement.tender.openeu.tests.question_blanks import (
    # TenderQuestionResourceTest
    patch_tender_question as patch_tender_question_eu,
)

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogUAContentWebTest,
    BaseCompetitiveDialogEUContentWebTest,
    test_lots,
    test_bids
)
from openprocurement.tender.competitivedialogue.tests.stage1.question_blanks import (
    # CompetitiveDialogEUQuestionResourceTest
    create_tender_question_invalid_eu,
    create_tender_question_eu,
    get_tender_question_eu,
    get_tender_questions_eu,
)


class CompetitiveDialogUAQuestionResourceTest(BaseCompetitiveDialogUAContentWebTest, TenderQuestionResourceTestMixin):

    test_create_tender_question = snitch(create_tender_question_ua)
    test_patch_tender_question = snitch(patch_tender_question)


class CompetitiveDialogUAQLotQuestionResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = 2 * test_lots
    author_data = test_bids[0]["tenderers"][0]

    test_create_tender_question = snitch(lot_create_tender_question)
    test_patch_tender_question = snitch(lot_patch_tender_question)


class CompetitiveDialogEUQuestionResourceTest(BaseCompetitiveDialogEUContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids  # TODO: change attribute identifier
    author_data = test_bids[0]["tenderers"][0]

    test_create_tender_question_invalid = snitch(create_tender_question_invalid_eu)
    test_create_tender_question = snitch(create_tender_question_eu)
    test_patch_tender_question = snitch(patch_tender_question_eu)
    test_get_tender_question = snitch(get_tender_question_eu)
    test_get_tender_questions = snitch(get_tender_questions_eu)


class CompetitiveDialogEULotQuestionResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids  # TODO: change attribute identifier
    author_data = test_bids[0]["tenderers"][0]

    test_create_tender_question = snitch(lot_create_tender_question)
    test_patch_tender_question = snitch(lot_patch_tender_question)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogUAQuestionResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUQuestionResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUAQLotQuestionResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEULotQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
