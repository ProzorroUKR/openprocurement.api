# -*- coding: utf-8 -*-
import unittest

from datetime import datetime, timedelta
from openprocurement.api.models import get_now
from openprocurement.api.tests.base import test_organization
from openprocurement.tender.competitivedialogue.tests.base import (test_tender_data_ua, test_bids,
                                                                   BaseCompetitiveDialogUAContentWebTest,
                                                                   BaseCompetitiveDialogEUContentWebTest, test_lots)


class CompetitiveDialogUAQuestionResourceTest(BaseCompetitiveDialogUAContentWebTest):

    def test_create_tender_question_invalid(self):
        """
          Try create invalid question
        """

        # Try create question with bad token id
        response = self.app.post_json('/tenders/some_id/questions', {
                                      'data': {'title': 'question title',
                                               'description': 'question description',
                                               'author': test_organization}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/questions'.format(self.tender_id)
        # Try create question with bad content_type
        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']",
             u'location': u'header', u'name': u'Content-Type'}
        ])

        # Try create question with bad json object
        response = self.app.post(
            request_path, 'data', content_type='application/json', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'No JSON object could be decoded',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create question with with bad content type, and bad json
        response = self.app.post_json(request_path, 'data', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create question with invalid data
        response = self.app.post_json(
            request_path, {'not_data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create question with without required fields
        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'author'},
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'title'},
        ])

        # Try create question with unnecessary fields
        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        # Try create question with bad author fields
        response = self.app.post_json(request_path, {'data': {'author': {'identifier': 'invalid_value'}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'identifier': [u'Please use a mapping for this field or Identifier instance instead of unicode.']}, u'location': u'body', u'name': u'author'}
        ])

        # Try create question without required fields
        response = self.app.post_json(request_path,
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': {'identifier': {}}}
                                       },
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

        # Try create question without required fields, and invalid uri field
        response = self.app.post_json(request_path,
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': {'name': 'name',
                                                           'identifier': {'uri': 'invalid_value'}}}
                                       },
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
             u'location': u'body',
             u'name': u'author'}
        ])

        # Try create question without required fields(description)
        response = self.app.post_json(request_path,
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_organization,
                                                'questionOf': 'lot'}
                                       },
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'],
             u'location': u'body',
             u'name': u'relatedItem'}
        ])

        # Try create question with invalid relatedItem
        response = self.app.post_json(request_path,
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_organization,
                                                'questionOf': 'lot',
                                                'relatedItem': '0' * 32}
                                       },
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
        ])

    def test_create_tender_question(self):
        """
            Create question
        """
        # Create path for good request
        request_path = '/tenders/{}/questions'.format(self.tender_id)

        # Create question and check response fields, they must match
        response = self.app.post_json(request_path,
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_organization}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], test_organization['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

        self.go_to_enquiryPeriod_end()
        # Try add question after when endquiryPeriod end
        response = self.app.post_json(request_path,
                                      {'data': {'title':
                                                'question title',
                                                'description': 'question description',
                                                'author': test_organization}
                                       }, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add question only in enquiryPeriod')

    def test_patch_tender_question(self):
        """
            Test path question
        """

        # Create question
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_organization}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        # Answer on question
        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(
            self.tender_id, question['id'], self.tender_token), {'data': {'answer': 'answer'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['answer'], 'answer')

        # Try answer on question that doesn't exists
        response = self.app.patch_json('/tenders/{}/questions/some_id'.format(self.tender_id),
                                       {'data': {'answer': 'answer'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'question_id'}
        ])

        # Try answer on question that doesn't exists, and tender too
        response = self.app.patch_json('/tenders/some_id/questions/some_id', {'data': {'answer': 'answer'}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Get answer by tender_id, and question_id
        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['answer'], 'answer')

    def test_get_tender_question(self):
        """
            Test get question
        """

        # Create question
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_organization}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        # Get question by tender_id, and question_id
        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data']), set([u'id', u'date', u'title', u'description', u'questionOf']))

        # TODO: Not sure that we can answer on question in qualification period
        self.set_status('active.qualification')

        # Get question which in active.qualification
        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], question)

        # Try get question with bad question_id
        response = self.app.get('/tenders/{}/questions/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'question_id'}
        ])

        # Try get question with bad tender_id and question_id
        response = self.app.get('/tenders/some_id/questions/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_questions(self):
        """
          Test get questions
        """

        # Create question
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_organization}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        # Get all questions by tender_id
        response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'date', u'title', u'description', u'questionOf']))

        self.set_status('active.qualification')

        # Get all questions for tender which in activate.qualification status
        response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], question)

        # Try get questions with bad tender_id
        response = self.app.get('/tenders/some_id/questions', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])


class CompetitiveDialogUAQLotQuestionResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = 2 * test_lots

    def test_create_tender_question(self):
        """
            Test the creating question on cancel and activate lots
        """

        # Cancel lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': self.initial_lots[0]['id']}
                                       })
        self.assertEqual(response.status, '201 Created')

        # Try create question with link on cancel lot
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.initial_lots[0]['id'],
                                                'author': test_organization}
                                       }, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add question only in active lot status')

        # Create question on activate lot
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.initial_lots[1]['id'],
                                                'author': test_organization}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], test_organization['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

    def test_patch_tender_question(self):
        """
            Test the adding answer on lot which was close

        """
        # Create question on lot
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.initial_lots[0]['id'],
                                                'author': test_organization}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        # Cancel lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': self.initial_lots[0]['id']
                                                }
                                       })
        self.assertEqual(response.status, '201 Created')

        # Try add answer on lot which are cancel
        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {'data': {'answer': 'answer'}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update question only in active lot status')

        # Create question on lot which has status active
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.initial_lots[1]['id'],
                                                'author': test_organization}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        # Create answer on question, lot has status active
        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {'data': {'answer': 'answer'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['answer'], 'answer')

        # Get answer by question id
        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['answer'], 'answer')


class CompetitiveDialogUEQuestionResourceTest(BaseCompetitiveDialogEUContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_question_invalid(self):
        """
          Test the creating invalid question
        """

        # Try create question with invalid tender_id
        response = self.app.post_json('/tenders/some_id/questions',
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_bids[0]['tenderers'][0]}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/questions'.format(self.tender_id)

        # Try create question without content_type
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

        # Try create question with bad json
        response = self.app.post(request_path, 'data', content_type='application/json', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'No JSON object could be decoded',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create question with bad json
        response = self.app.post_json(request_path, 'data', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create question with invalid json
        response = self.app.post_json(request_path, {'not_data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create question without required fields
        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'author'},
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'title'},
        ])

        # Try create question with invalid fields
        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        # Try create question with invalid identifier
        response = self.app.post_json(request_path, {'data': {'author': {'identifier': 'invalid_value'}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'identifier': [u'Please use a mapping for this field or Identifier instance instead of unicode.']}, u'location': u'body', u'name': u'author'}
        ])

        # Try create question without required fields
        response = self.app.post_json(request_path,
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': {'identifier': {}}}
                                       },
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':{u'contactPoint': [u'This field is required.'],
                             u'identifier': {u'scheme': [u'This field is required.'],
                                             u'id': [u'This field is required.']},
                             u'name': [u'This field is required.'],
                             u'address': [u'This field is required.']},
             u'location': u'body', u'name': u'author'}
        ])

        # Try create question without required fields and with invalid identifier.uri
        response = self.app.post_json(request_path,
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': {'name': 'name',
                                                           'identifier': {'uri': 'invalid_value'}}
                                                }
                                       },
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

        # Try create question without required field(description)
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_bids[0]['tenderers'][0],
                                                'questionOf': 'lot'}
                                       },
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedItem'}
        ])

        # Try create question with bad relatedItem id
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_bids[0]['tenderers'][0],
                                                'questionOf': 'lot',
                                                'relatedItem': '0' * 32}
                                       },
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
        ])

    def test_create_tender_question(self):
        """
          Create question with many posible ways
        """

        # Create question, and check fields match
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_bids[0]['tenderers'][0]}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], test_bids[0]['tenderers'][0]['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

        # Shift time to end of enquiry period
        self.time_shift('enquiryPeriod_ends')

        # Try create question, when enquiry period end
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_bids[0]['tenderers'][0]}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add question only in enquiryPeriod')

        self.time_shift('active.pre-qualification')  # Shift time to status active.pre-qualification
        self.check_chronograph()

        # Try create question when tender in status active.pre-qualification
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_bids[0]['tenderers'][0]}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add question only in enquiryPeriod')

    def test_patch_tender_question(self):
        """
          Test the patching questions
        """

        # Create question
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_bids[0]['tenderers'][0]}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']  # Save question in local namespace

        # Add answer on question which we make
        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {'data': {'answer': 'answer'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['answer'], 'answer')

        # Try add answer, by bad token_id
        response = self.app.patch_json('/tenders/{}/questions/some_id'.format(self.tender_id),
                                       {'data': {'answer': 'answer'}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'question_id'}
        ])

        # Try add answer, by bad token_id, and bad question_id
        response = self.app.patch_json('/tenders/some_id/questions/some_id', {'data': {'answer': 'answer'}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Add answer by good token_id, and question_id
        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['answer'], 'answer')

        # Shift time to tender status active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()  # check chronograph

        # Try add question when tender status unsuccessful
        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {'data': {'answer': 'answer'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't update question in current (unsuccessful) tender status")

    def test_get_tender_question(self):
        """
          Try get tender question
        """
        # Create question
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_bids[0]['tenderers'][0]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']  # save question

        # Get question by tender_id, and question_id
        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data']), set([u'id', u'date', u'title', u'description', u'questionOf']))

        # Add answer to question
        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {'data': {'answer': 'answer'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['answer'], 'answer')
        question['answer'] = 'answer'

        self.time_shift('active.pre-qualification')  # Shift time tender to status active.pre-qualification
        self.check_chronograph()

        # Get question by token_id, and question_id
        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], question)

        # Try get question by bad question_id
        response = self.app.get('/tenders/{}/questions/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'question_id'}
        ])

        # Try get question by bad token_id, and question_id
        response = self.app.get('/tenders/some_id/questions/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_questions(self):
        """
          Test the get questions
        """
        # Create question
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'author': test_bids[0]['tenderers'][0]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        # Get question
        response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'date', u'title', u'description', u'questionOf']))

        # Add answer on question
        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {'data': {'answer': 'answer'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['answer'], 'answer')
        question['answer'] = 'answer'

        self.time_shift('active.pre-qualification')  # Shift time to tender status active.pre-qualification
        self.check_chronograph()

        # Try get questions by tender_id
        response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], question)

        # Try get question by bad tender_id
        response = self.app.get('/tenders/some_id/questions', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])


class CompetitiveDialogUELotQuestionResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_question(self):
        # Cancel lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': self.initial_lots[0]['id']}
                                       })
        self.assertEqual(response.status, '201 Created')

        # Try create question to cancel lot
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.initial_lots[0]['id'],
                                                'author': test_bids[0]['tenderers'][0]}
                                       },
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add question only in active lot status')

        # Create question for active lot
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.initial_lots[1]['id'],
                                                'author': test_bids[0]['tenderers'][0]}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], test_bids[0]['tenderers'][0]['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

    def test_patch_tender_question(self):
        """
            Test the patching question on lot
        """
        # Create question on lot
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.initial_lots[0]['id'],
                                                'author': test_bids[0]['tenderers'][0]}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        # Cancel lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': self.initial_lots[0]['id']}
                                       })
        self.assertEqual(response.status, '201 Created')

        # Try add answer to question, when lot is cancel
        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {'data': {'answer': 'answer'}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update question only in active lot status')

        # Create question to active lot
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.initial_lots[1]['id'],
                                                'author': test_bids[0]['tenderers'][0]}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        # Add answer to question on active lot
        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id,
                                                                                      question['id'],
                                                                                      self.tender_token),
                                       {'data': {'answer': 'answer'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['answer'], 'answer')

        # Get question on active lot
        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['answer'], 'answer')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogUAQuestionResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUEQuestionResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUAQLotQuestionResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUELotQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
