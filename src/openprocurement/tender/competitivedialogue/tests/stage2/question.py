# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.question_blanks import (
    create_tender_question_invalid,
    patch_tender_question,
    lot_create_tender_question,
    lot_patch_tender_question,
)

from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_cd_lots,
    test_tender_cd_author,
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
)
from openprocurement.tender.competitivedialogue.tests.stage1.question_blanks import (
    get_tender_question_eu as get_tender_question,
    get_tender_questions_eu as get_tender_questions,
)
from openprocurement.tender.competitivedialogue.tests.stage2.question_blanks import (
    create_question_bad_author,
    create_tender_question_with_question,
    create_tender_question,
    lot_create_tender_question_without_perm,
    lot_create_tender_question_on_item,
    create_tender_question_on_item,
)

from openprocurement.tender.openeu.tests.base import test_tender_openeu_bids


class TenderStage2QuestionResourceTestMixin:

    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identifier
    author_data = test_tender_cd_author  # TODO: change attribute identifier

    test_create_tender_question_invalid = snitch(create_tender_question_invalid)
    test_create_question_bad_author = snitch(create_question_bad_author)
    test_create_tender_question_with_questionOf = snitch(create_tender_question_with_question)
    test_create_tender_question = snitch(create_tender_question)
    test_create_tender_question_on_item = snitch(create_tender_question_on_item)
    test_patch_tender_question = snitch(patch_tender_question)
    test_get_tender_question = snitch(get_tender_question)
    test_get_tender_questions = snitch(get_tender_questions)


class TenderStage2EUQuestionResourceTest(
    TenderStage2QuestionResourceTestMixin,
    BaseCompetitiveDialogEUStage2ContentWebTest,
):
    pass


class TenderStage2UAQuestionResourceTest(
    TenderStage2QuestionResourceTestMixin,
    BaseCompetitiveDialogUAStage2ContentWebTest,
):
    pass


class TenderStage2LotQuestionResourceTestMixin:

    initial_lots = 2 * test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identifier
    author_data = test_tender_cd_author  # TODO: change attribute identifier

    test_create_tender_question = snitch(lot_create_tender_question)
    test_create_tender_question_without_perm = snitch(lot_create_tender_question_without_perm)
    test_create_tender_question_on_item = snitch(lot_create_tender_question_on_item)
    test_patch_tender_question = snitch(lot_patch_tender_question)


class TenderStage2EULotQuestionResourceTest(
    TenderStage2LotQuestionResourceTestMixin,
    BaseCompetitiveDialogEUStage2ContentWebTest,
):
    pass


class TenderStage2UALotQuestionResourceTest(
    TenderStage2LotQuestionResourceTestMixin,
    BaseCompetitiveDialogUAStage2ContentWebTest,
):
    pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotQuestionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
