# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_lots, test_organization
)
from openprocurement.tender.belowthreshold.tests.question import TenderQuestionResourceTestMixin
from openprocurement.tender.belowthreshold.tests.question_blanks import (
    # TenderQuestionResourceTest
    patch_tender_question,
    # TenderLotQuestionResourceTest
    lot_create_tender_question,
)

from openprocurement.tender.openua.tests.question_blanks import (
    # TenderQuestionResourceTest
    create_tender_question,
)

from openprocurement.tender.openuadefense.tests.base import BaseTenderUAContentWebTest
from openprocurement.tender.openuadefense.tests.question_blanks import (
    # TenderLotQuestionResourceTest
    patch_multilot_tender_question,
)


class TenderQuestionResourceTest(BaseTenderUAContentWebTest, TenderQuestionResourceTestMixin):

    test_create_tender_question = snitch(create_tender_question)
    test_patch_tender_question = snitch(patch_tender_question)


class TenderLotQuestionResourceTest(BaseTenderUAContentWebTest):

    initial_lots = 2 * test_lots
    author_data = test_organization

    test_create_tender_question = snitch(lot_create_tender_question)
    test_patch_tender_question = snitch(patch_multilot_tender_question)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
