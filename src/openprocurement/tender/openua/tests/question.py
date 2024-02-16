import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.question import (
    TenderQuestionResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.question_blanks import (
    create_tender_question,
    lot_create_tender_question,
    lot_patch_tender_question,
    lot_patch_tender_question_lots_none,
    patch_tender_question,
)
from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest
from openprocurement.tender.openua.tests.question_blanks import (
    item_has_unanswered_questions,
    lot_has_unanswered_questions,
    tender_has_unanswered_questions,
)


class TenderQuestionResourceTest(BaseTenderUAContentWebTest, TenderQuestionResourceTestMixin):
    test_create_tender_question = snitch(create_tender_question)
    test_patch_tender_question = snitch(patch_tender_question)


class TenderLotQuestionResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_tender_below_lots
    author_data = test_tender_below_author

    def create_question_for(self, questionOf, relatedItem):
        response = self.app.post_json(
            "/tenders/{}/questions".format(self.tender_id),
            {
                "data": {
                    "title": "question title",
                    "description": "question description",
                    "questionOf": questionOf,
                    "relatedItem": relatedItem,
                    "author": test_tender_below_author,
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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderQuestionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotQuestionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
