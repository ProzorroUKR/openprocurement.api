# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from uuid import uuid4

from openprocurement.tender.competitivedialogue.tests.base import (test_lots, test_bids, test_shortlistedFirms,
                                                                   BaseCompetitiveDialogEUStage2ContentWebTest,
                                                                   BaseCompetitiveDialogUAStage2ContentWebTest)

author = test_bids[0]["tenderers"][0]
author['identifier']['id'] = test_shortlistedFirms[0]['identifier']['id']
author['identifier']['scheme'] = test_shortlistedFirms[0]['identifier']['scheme']


class TenderStage2EUQuestionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_question_invalid(self):
        response = self.app.post_json('/tenders/some_id/questions',
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}},
                                      status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/questions'.format(self.tender_id)

        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']",
             u'location': u'header',
             u'name': u'Content-Type'}
        ])

        response = self.app.post(
            request_path, 'data', content_type='application/json', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'No JSON object could be decoded',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, 'data', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, {'not_data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'author'},
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'title'},
        ])

        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        response = self.app.post_json(request_path, {'data': {'author': {'identifier': 'invalid_value'}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'identifier': [u'Please use a mapping for this field or Identifier instance instead of unicode.']},
             u'location': u'body',
             u'name': u'author'}
        ])

        response = self.app.post_json(request_path, {'data': {'title': 'question title',
                                                              'description': 'question description',
                                                              'author': {'identifier': {}}}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': [u'This field is required.'],
                              u'identifier': {u'scheme': [u'This field is required.'],
                                              u'id': [u'This field is required.']},
                              u'name': [u'This field is required.'],
                              u'address': [u'This field is required.']},
             u'location': u'body',
             u'name': u'author'}
        ])

        response = self.app.post_json(request_path, {'data': {'title': 'question title',
                                                              'description': 'question description',
                                                              'author': {'name': 'name',
                                                                         'identifier': {'uri': 'invalid_value'}}}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': [u'This field is required.'],
                              u'identifier': {u'scheme': [u'This field is required.'],
                                              u'id': [u'This field is required.'],
                                              u'uri': [u'Not a well formed URL.']},
                              u'address': [u'This field is required.']},
             u'location': u'body', u'name': u'author'}
        ])

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author,
                                                "questionOf": "lot"}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'],
             u'location': u'body',
             u'name': u'relatedItem'}
        ])

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author,
                                                'questionOf': 'lot',
                                                'relatedItem': '0' * 32}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of lots'],
             u'location': u'body',
             u'name': u'relatedItem'}
        ])

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author,
                                                'questionOf': 'item',
                                                'relatedItem': '0' * 32}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of items'],
             u'location': u'body',
             u'name': u'relatedItem'}
        ])

        bad_author = deepcopy(author)
        good_id = bad_author['identifier']['id']
        good_scheme = author['identifier']['scheme']
        bad_author['identifier']['id'] = '12345'
        response = self.app.post_json(request_path,
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': bad_author}},
                                      status=403)

        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Author can\'t create question', u'location': u'body', u'name': u'author'}
        ])
        bad_author['identifier']['id'] = good_id
        bad_author['identifier']['scheme'] = 'XI-IATI'
        response = self.app.post_json(request_path,
                                      {'data': {'title': 'question title',
                                                'description': 'question descriptionn',
                                                'author': bad_author}},
                                      status=403)

        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Author can\'t create question', u'location': u'body', u'name': u'author'}])

    def test_create_tender_question_with_questionOf(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author,
                                                'questionOf': 'tender',
                                                'relatedItem': self.tender_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], author['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

        self.time_shift('enquiryPeriod_ends')

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

    def test_create_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], author['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

        self.time_shift('enquiryPeriod_ends')

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

    def test_patch_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")

        response = self.app.patch_json('/tenders/{}/questions/some_id'.format(self.tender_id),
                                       {"data": {"answer": "answer"}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'question_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/questions/some_id', {"data": {"answer": "answer"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update question in current (unsuccessful) tender status")

    def test_get_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data']), set([u'id', u'date', u'title', u'description', u'questionOf']))

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")
        self.assertIn('dateAnswered', response.json['data'])
        question["answer"] = "answer"
        question['dateAnswered'] = response.json['data']['dateAnswered']

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], question)

        response = self.app.get('/tenders/{}/questions/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'question_id'}
        ])

        response = self.app.get('/tenders/some_id/questions/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_questions(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'date', u'title', u'description', u'questionOf']))

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")
        self.assertIn('dateAnswered', response.json['data'])
        question["answer"] = "answer"
        question['dateAnswered'] = response.json['data']['dateAnswered']

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], question)

        response = self.app.get('/tenders/some_id/questions', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def create_question_on_item(self):
        tender = self.db.get(self.tender_id)
        item = tender['items'][0]
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'item',
                                                'relatedItem': item['id'],
                                                'author': author}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'tender',
                                                'author': author}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')


class TenderStage2EULotQuestionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_question(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.lots[0]['id'],
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can add question only in active lot status")

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.lots[1]['id'],
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], test_bids[0]['tenderers'][0]['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

    def test_create_question_on_lot_without_perm(self):
        tender = self.db.get(self.tender_id)
        lot_id = self.lots[0]['id']
        for firm in tender['shortlistedFirms']:
            firm['lots'] = [{'id': self.lots[1]['id']}]
        self.db.save(tender)

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': lot_id,
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Author can\'t create question',
             u'location': u'body',
             u'name': u'author'}
        ])

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
                                                'author': author}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        # Can't create question on item, on which we haven't access
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'item',
                                                'relatedItem': item['id'],
                                                'author': author}},
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
                                                'author': author}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

    def test_patch_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.lots[0]['id'],
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can update question only in active lot status")

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.lots[1]['id'],
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")

        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")


class TenderStage2UAQuestionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_question_invalid(self):
        response = self.app.post_json('/tenders/some_id/questions',
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}},
                                      status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/questions'.format(self.tender_id)

        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']",
             u'location': u'header',
             u'name': u'Content-Type'}
        ])

        response = self.app.post(
            request_path, 'data', content_type='application/json', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'No JSON object could be decoded',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, 'data', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, {'not_data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'author'},
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'title'},
        ])

        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        response = self.app.post_json(request_path, {'data': {'author': {'identifier': 'invalid_value'}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'identifier': [u'Please use a mapping for this field or Identifier instance instead of unicode.']},
             u'location': u'body',
             u'name': u'author'}
        ])

        response = self.app.post_json(request_path, {'data': {'title': 'question title',
                                                              'description': 'question description',
                                                              'author': {'identifier': {}}}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': [u'This field is required.'],
                              u'identifier': {u'scheme': [u'This field is required.'],
                                              u'id': [u'This field is required.']},
                              u'name': [u'This field is required.'],
                              u'address': [u'This field is required.']},
             u'location': u'body',
             u'name': u'author'}
        ])

        response = self.app.post_json(request_path, {'data': {'title': 'question title',
                                                              'description': 'question description',
                                                              'author': {'name': 'name',
                                                                         'identifier': {'uri': 'invalid_value'}}}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': [u'This field is required.'],
                              u'identifier': {u'scheme': [u'This field is required.'],
                                              u'id': [u'This field is required.'],
                                              u'uri': [u'Not a well formed URL.']},
                              u'address': [u'This field is required.']},
             u'location': u'body', u'name': u'author'}
        ])

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author,
                                                "questionOf": "lot"}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'],
             u'location': u'body',
             u'name': u'relatedItem'}
        ])

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author,
                                                'questionOf': 'lot',
                                                'relatedItem': '0' * 32}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of lots'],
             u'location': u'body',
             u'name': u'relatedItem'}
        ])

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author,
                                                'questionOf': 'item',
                                                'relatedItem': '0' * 32}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of items'],
             u'location': u'body',
             u'name': u'relatedItem'}
        ])

        bad_author = deepcopy(author)
        good_id = bad_author['identifier']['id']
        good_scheme = author['identifier']['scheme']
        bad_author['identifier']['id'] = '12345'
        response = self.app.post_json(request_path,
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': bad_author}},
                                      status=403)

        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Author can\'t create question', u'location': u'body', u'name': u'author'}
        ])
        bad_author['identifier']['id'] = good_id
        bad_author['identifier']['scheme'] = 'XI-IATI'
        response = self.app.post_json(request_path,
                                      {'data': {'title': 'question title',
                                                'description': 'question descriptionn',
                                                'author': bad_author}},
                                      status=403)

        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Author can\'t create question', u'location': u'body', u'name': u'author'}])

    def test_create_tender_question_with_questionOf(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author,
                                                'questionOf': 'tender',
                                                'relatedItem': self.tender_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], author['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

        self.time_shift('enquiryPeriod_ends')

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

    def test_create_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], author['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

        self.time_shift('enquiryPeriod_ends')

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

    def test_patch_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")

        response = self.app.patch_json('/tenders/{}/questions/some_id'.format(self.tender_id),
                                       {"data": {"answer": "answer"}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'question_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/questions/some_id', {"data": {"answer": "answer"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update question in current (unsuccessful) tender status")

    def test_get_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data']), set([u'id', u'date', u'title', u'description', u'questionOf']))

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")
        self.assertIn('dateAnswered', response.json['data'])
        question["answer"] = "answer"
        question['dateAnswered'] = response.json['data']['dateAnswered']

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], question)

        response = self.app.get('/tenders/{}/questions/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'question_id'}
        ])

        response = self.app.get('/tenders/some_id/questions/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_questions(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'date', u'title', u'description', u'questionOf']))

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")
        self.assertIn('dateAnswered', response.json['data'])
        question["answer"] = "answer"
        question['dateAnswered'] = response.json['data']['dateAnswered']

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], question)

        response = self.app.get('/tenders/some_id/questions', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def create_question_on_item(self):
        tender = self.db.get(self.tender_id)
        item = tender['items'][0]
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'item',
                                                'relatedItem': item['id'],
                                                'author': author}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'tender',
                                                'author': author}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')


class TenderStage2UALotQuestionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_question(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.lots[0]['id'],
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can add question only in active lot status")

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.lots[1]['id'],
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], test_bids[0]['tenderers'][0]['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

    def test_create_question_on_lot_without_perm(self):
        tender = self.db.get(self.tender_id)
        lot_id = self.lots[0]['id']
        for firm in tender['shortlistedFirms']:
            firm['lots'] = [{'id': self.lots[1]['id']}]
        self.db.save(tender)

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': lot_id,
                                                'author': author}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Author can\'t create question',
             u'location': u'body',
             u'name': u'author'}
        ])

    def test_patch_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.lots[0]['id'],
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can update question only in active lot status")

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.lots[1]['id'],
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {"data": {"answer": "answer"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")

        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")

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
                                                'author': author}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        # Can't create question on item, on which we haven't access
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'item',
                                                'relatedItem': item['id'],
                                                'author': author}},
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
                                                'author': author}})

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
