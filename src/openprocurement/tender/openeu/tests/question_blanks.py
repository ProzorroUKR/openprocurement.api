# -*- coding: utf-8 -*-
# TenderQuestionResourceTest


def patch_tender_question(self):
    response = self.app.post_json('/tenders/{}/questions'.format(
        self.tender_id), {'data': {'title': 'question title', 'description': 'question description',
                                   'author': self.test_bids_data[0]['tenderers'][0]}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']

    response = self.app.patch_json(
        '/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id, question['id'], self.tender_token),
        {"data": {"answer": "answer"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["answer"], "answer")

    response = self.app.patch_json('/tenders/{}/questions/some_id'.format(self.tender_id),
                                   {"data": {"answer": "answer"}}, status=404)
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

    response = self.app.patch_json(
        '/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id, question['id'], self.tender_token),
        {"data": {"answer": "answer"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update question in current (unsuccessful) tender status")


def answering_question(self):
    response = self.app.post_json('/tenders/{}/questions'.format(
        self.tender_id), {'data': {'title': 'question title', 'description': 'question description',
                                   'author': self.test_bids_data[0]['tenderers'][0]}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']

    response = self.app.patch_json(
        '/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id, question['id'], self.tender_token),
        {"data": {"answer": "answer"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["answer"], "answer")
    self.assertIn('dateAnswered', response.json['data'])
    question["answer"] = "answer"
    question['dateAnswered'] = response.json['data']['dateAnswered']

    self.time_shift('active.pre-qualification')
    self.check_chronograph()
