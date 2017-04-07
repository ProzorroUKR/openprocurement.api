# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.tests.base import test_organization

# TenderLotQuestionResourceTest


def patch_multilot_tender_question(self):
    response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), {'data': {
        'title': 'question title',
        'description': 'question description',
        "questionOf": "lot",
        "relatedItem": self.initial_lots[0]['id'],
        'author': test_organization
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']

    response = self.app.post_json('/tenders/{}/cancellations'.format(self.tender_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.patch_json('/tenders/{}/questions/{}'.format(self.tender_id, question['id']), {"data": {"answer": "answer"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update question only in active lot status")

    response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), {'data': {
        'title': 'question title',
        'description': 'question description',
        "questionOf": "lot",
        "relatedItem": self.initial_lots[1]['id'],
        'author': test_organization
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']

    response = self.app.patch_json('/tenders/{}/questions/{}'.format(self.tender_id, question['id']), {"data": {"answer": "answer"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["answer"], "answer")

    response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["answer"], "answer")
