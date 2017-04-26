# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.question_blanks import (
    # TenderStage2QuestionResourceTest
    create_tender_question_invalid,
    # TenderStage2LotQuestionResourceTest
    lot_create_tender_question as create_tender_with_lots_question,
    lot_patch_tender_question as patch_tender_with_lots_question
)

from openprocurement.tender.openeu.tests.question_blanks import (
    # TenderStage2QuestionResourceTest
    patch_tender_question,
)

from openprocurement.tender.competitivedialogue.tests.base import (
    test_lots,
    test_shortlistedFirms,
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest
)
from openprocurement.tender.competitivedialogue.tests.stage1.question_blanks import (
    # TenderStage2QuestionResourceTest
    get_tender_question_eu as get_tender_question,
    get_tender_questions_eu as get_tender_questions,
)
from openprocurement.tender.competitivedialogue.tests.stage2.question_blanks import (
    # TenderStage2QuestionResourceTest
    create_question_bad_author,
    create_tender_question_with_question,
    create_tender_question,
    # TenderStage2LotQuestionResourceTest
    create_question_on_lot_without_perm,
)

from openprocurement.tender.openeu.tests.base import test_bids

author = test_bids[0]["tenderers"][0]
author['identifier']['id'] = test_shortlistedFirms[0]['identifier']['id']
author['identifier']['scheme'] = test_shortlistedFirms[0]['identifier']['scheme']


class TenderStage2EUQuestionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids  # TODO: change attribute identifier
    author_data = author  # TODO: change attribute identifier

    test_create_tender_question_invalid = snitch(create_tender_question_invalid)
    test_create_question_bad_author = snitch(create_question_bad_author)
    test_create_tender_question_with_questionOf = snitch(create_tender_question_with_question)
    test_create_tender_question = snitch(create_tender_question)
    test_patch_tender_question = snitch(patch_tender_question)
    test_get_tender_question = snitch(get_tender_question)
    test_get_tender_questions = snitch(get_tender_questions)

    #  TODO: fix test
    def create_question_on_item(self):
        tender = self.db.get(self.tender_id)
        item = tender['items'][0]
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'item',
                                                'relatedItem': item['id'],
                                                'author': self.author_data}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'tender',
                                                'author': self.author_data}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')


class TenderStage2EULotQuestionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids  # TODO: change attribute identifier
    author_data = author  # TODO: change attribute identifier

    test_create_tender_question = snitch(create_tender_with_lots_question)
    test_create_question_on_lot_without_perm = snitch(create_question_on_lot_without_perm)
    test_patch_tender_question = snitch(patch_tender_with_lots_question)

    #  TODO: fix test
    def create_question_on_item(self):
        tender = self.db.get(self.tender_id)
        item = tender['items'][0]
        new_item = deepcopy(item)
        new_item['id'] = uuid4().hex
        new_item['relatedLot'] = self.lots[1]['id']
        tender['items'] = [item, new_item]
        for firm in tender['shortlistedFirms']:
            firm['lots'] = [{'id': self.lots[1]['id']}]
        self.db.save(tender)

        # Create question on item
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'item',
                                                'relatedItem': new_item['id'],
                                                'author': self.author_data}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        # Can't create question on item, on which we haven't access
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'item',
                                                'relatedItem': item['id'],
                                                'author': self.author_data}},
                                      status=403)

        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Author can\'t create question',
             u'location': u'body',
             u'name': u'author'}
        ])

        # Create question on tender
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'tender',
                                                'author': self.author_data}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')


class TenderStage2UAQuestionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids  # TODO: change attribute identifier
    author_data = author  # TODO: change attribute identifier

    test_create_tender_question_invalid = snitch(create_tender_question_invalid)
    test_create_question_bad_author = snitch(create_question_bad_author)
    test_create_tender_question_with_questionOf = snitch(create_tender_question_with_question)
    test_create_tender_question = snitch(create_tender_question)
    test_patch_tender_question = snitch(patch_tender_question)
    test_get_tender_question = snitch(get_tender_question)
    test_get_tender_questions = snitch(get_tender_questions)

    #  TODO: fix test
    def create_question_on_item(self):
        tender = self.db.get(self.tender_id)
        item = tender['items'][0]
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'item',
                                                'relatedItem': item['id'],
                                                'author': self.author_data}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'tender',
                                                'author': self.author_data}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')


class TenderStage2UALotQuestionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids  # TODO: change attribute identifier
    author_data = author  # TODO: change attribute identifier

    test_create_tender_question = snitch(create_tender_with_lots_question)
    test_create_question_on_lot_without_perm = snitch(create_question_on_lot_without_perm)
    test_patch_tender_question = snitch(patch_tender_with_lots_question)

    #  TODO: fix test
    def create_question_on_item(self):
        tender = self.db.get(self.tender_id)
        item = tender['items'][0]
        new_item = deepcopy(item)
        new_item['id'] = uuid4().hex
        new_item['relatedLot'] = self.lots[1]['id']
        tender['items'] = [item, new_item]
        for firm in tender['shortlistedFirms']:
            firm['lots'] = [{'id': self.lots[1]['id']}]
        self.db.save(tender)

        # Create question on item
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'item',
                                                'relatedItem': new_item['id'],
                                                'author': self.author_data}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        # Can't create question on item, on which we haven't access
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'item',
                                                'relatedItem': item['id'],
                                                'author': self.author_data}},
                                      status=403)

        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Author can\'t create question',
             u'location': u'body',
             u'name': u'author'}
        ])

        # Create question on tender
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'tender',
                                                'author': self.author_data}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
