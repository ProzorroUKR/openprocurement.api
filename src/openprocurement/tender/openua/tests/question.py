# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_lots, test_author

from openprocurement.tender.belowthreshold.tests.question import TenderQuestionResourceTestMixin
from openprocurement.tender.belowthreshold.tests.question_blanks import (
    # TenderLotQuestionResourceTest
    lot_create_tender_question,
    lot_patch_tender_question,
    lot_patch_tender_question_lots_none,
    # TenderQuestionResourceTest
    patch_tender_question,
)

from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest
from openprocurement.tender.openua.tests.question_blanks import (
    # TenderQuestionResourceTest
    create_tender_question,
    # TenderLotQuestionResourceTest
    tender_has_unanswered_questions,
    lot_has_unanswered_questions,
    item_has_unanswered_questions,
)


class TenderQuestionResourceTest(BaseTenderUAContentWebTest, TenderQuestionResourceTestMixin):
    test_create_tender_question = snitch(create_tender_question)
    test_patch_tender_question = snitch(patch_tender_question)


class TenderLotQuestionResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_lots
    author_data = test_author

    def create_question_for(self, questionOf, relatedItem):
        response = self.app.post_json(
            "/tenders/{}/questions".format(self.tender_id),
            {
                "data": {
                    "title": "question title",
                    "description": "question description",
                    "questionOf": questionOf,
                    "relatedItem": relatedItem,
                    "author": test_author,
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        return response.json["data"]["id"]

    test_create_tender_lot_question = snitch(lot_create_tender_question)
    test_patch_tender_lot_question = snitch(lot_patch_tender_question)
    test_tender_has_unanswered_questions = snitch(tender_has_unanswered_questions)
    test_lot_has_unanswered_questions = snitch(lot_has_unanswered_questions)
    test_item_has_unanswered_questions = snitch(item_has_unanswered_questions)
    test_lot_patch_tender_question_lots_none = snitch(lot_patch_tender_question_lots_none)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotQuestionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
