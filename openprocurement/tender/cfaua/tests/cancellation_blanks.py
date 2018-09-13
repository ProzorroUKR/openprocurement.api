# -*- coding: utf-8 -*-
import jmespath


def assert_statuses(self, rules={}):
    data = self.get_tender(role='broker').json
    for rule in rules:
        value = jmespath.search(rule, data)
        self.assertEqual(value, rules[rule])


def add_tender_complaints(self, statuses):
    # ['satisfied', 'stopped', 'declined', 'mistaken', 'invalid']
    for status in statuses:
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), {
            'data': {
                'title': 'complaint title',
                'description': 'complaint description',
                'author': self.test_author,
                'status': 'pending',
            }
        })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']
        url_patch_complaint = '/tenders/{}/complaints/{}'.format(self.tender_id, complaint['id'])
        response = self.app.patch_json('{}?acc_token={}'.format(url_patch_complaint, owner_token), {
            'data': {
                'status': 'stopping',
                'cancellationReason': 'reason',
            }
        })
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'stopping')
        self.assertEqual(response.json['data']['cancellationReason'], 'reason')

        self.app.authorization = ('Basic', ('reviewer', ''))
        response = self.app.patch_json(url_patch_complaint, {
            'data': {
                'decision': 'decision',
                'status': status,
            }
        })
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], status)
        self.assertEqual(response.json['data']['decision'], 'decision')
        self.app.authorization = ('Basic', ('broker', ''))


def cancellation_tender_active_tendering(self):
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    response = self.app.post_json('/tenders/{}/complaints'.format(
        self.tender_id), {
        'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.test_author,
                 'status': 'claim'}})
    self.assertEqual(response.status, '201 Created')
    self.cancel_tender()
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['active'],
            'data.bids[*].status': None,
            'data.qualifications[*].status': None,
            'data.awards[*].status': None,
            'data.agreements[*].status': None,
            'data.complaints[*].status': ['claim']
        })


def cancellation_tender_active_pre_qualification(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.tendering', 'end')
    self.check_chronograph()
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.pre-qualification')
    self.cancel_tender()
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['active'],
            'data.bids[*].status': ['invalid.pre-qualification', 'invalid.pre-qualification',
                                    'invalid.pre-qualification'],
            'data.qualifications[*].status': ['pending', 'pending', 'pending'],
            'data.awards[*].status': None,
            'data.agreements[*].status': None,
            'data.complaints[*].status':  ['invalid', 'stopped', 'mistaken']
        })


def cancellation_tender_active_pre_qualification_stand_still(self):
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    response = self.app.post_json('/tenders/{}/complaints'.format(
        self.tender_id), {
        'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.test_author,
                 'status': 'pending'}})
    self.assertEqual(response.status, '201 Created')
    complaint_id = response.json['data']['id']
    self.set_status('active.tendering', 'end')
    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json('/tenders/{}/complaints/{}'.format(
        self.tender_id, complaint_id), {'data': {'status': 'invalid'}}
    )
    self.assertEqual(response.status, '200 OK')
    self.check_chronograph()
    self.set_status('active.pre-qualification.stand-still')
    response = self.get_tender(role='broker')
    qualification_id = response.json['data']['qualifications'][0]['id']
    owner_token = self.initial_bids_tokens[response.json['data']['bids'][0]['id']]
    self.app.authorization = ('Basic', ('broker', ''))

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.pre-qualification.stand-still')

    response = self.app.post_json('/tenders/{0}/qualifications/{1}/complaints?acc_token={2}'.format(
        self.tender_id, qualification_id, owner_token), {
        'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.test_author,
                 'status': 'pending'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'pending')
    self.cancel_tender()
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['active'],
            'data.bids[*].status': ['invalid.pre-qualification', 'invalid.pre-qualification',
                                    'invalid.pre-qualification'],
            'data.qualifications[*].status': ['active', 'active', 'active'],
            'data.awards[*].status': None,
            'data.agreements[*].status': None,
            'data.complaints[*].status': ['invalid']

        })
    response = self.get_tender(role='broker')
    for qualification in response.json['data']['qualifications']:
        if qualification['id'] == qualification_id:
            self.assertEqual(qualification['complaints'][0]['status'], 'pending')


def cancellation_tender_active_auction(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.pre-qualification.stand-still')
    response = self.get_tender(role='broker')
    qualification_id = response.json['data']['qualifications'][0]['id']
    owner_token = self.initial_bids_tokens[response.json['data']['bids'][0]['id']]

    response = self.app.post_json('/tenders/{0}/qualifications/{1}/complaints?acc_token={2}'.format(
        self.tender_id, qualification_id, owner_token), {
        'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.test_author,
                 'status': 'pending'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'pending')

    self.set_status('active.auction')
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.auction')
    self.cancel_tender()
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['active'],
            'data.bids[*].status': ['invalid.pre-qualification', 'invalid.pre-qualification',
                                    'invalid.pre-qualification'],
            'data.qualifications[*].status': ['active', 'active', 'active'],
            'data.awards[*].status': None,
            'data.agreements[*].status': None,
            'data.complaints[*].status': ['invalid', 'stopped', 'mistaken']

        })
    response = self.get_tender(role='broker')
    for qualification in response.json['data']['qualifications']:
        if qualification['id'] == qualification_id:
            self.assertEqual(qualification['complaints'][0]['status'], 'pending')


def cancellation_tender_active_qualification(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.qualification')
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.qualification')
    self.cancel_tender()
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['active'],
            'data.bids[*].status': ['active', 'active', 'active'],
            'data.qualifications[*].status': ['active', 'active', 'active'],
            'data.awards[*].status': ['pending', 'pending', 'pending'],
            'data.agreements[*].status': None,
            'data.complaints[*].status': ['invalid', 'stopped', 'mistaken']
        })


def cancellation_tender_active_qualification_stand_still(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.qualification.stand-still')
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.qualification.stand-still')
    award_id = response.json['data']['awards'][0]['id']
    owner_token = self.initial_bids_tokens[response.json['data']['bids'][0]['id']]
    response = self.app.post_json('/tenders/{0}/awards/{1}/complaints?acc_token={2}'.format(
        self.tender_id, award_id, owner_token), {
        'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.test_author,
                 'status': 'pending'}})
    self.assertEqual(response.status, '201 Created')
    self.set_status('active.qualification.stand-still', 'end')
    self.check_chronograph()
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.qualification.stand-still')
    self.cancel_tender()
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['active'],
            'data.bids[*].status': ['active', 'active', 'active'],
            'data.qualifications[*].status': ['active', 'active', 'active'],
            'data.awards[*].status': ['active', 'active', 'active'],
            'data.agreements[*].status': None,
            'data.complaints[*].status': ['invalid', 'stopped', 'mistaken']
        })
    response = self.get_tender(role='broker')
    for award in response.json['data']['awards']:
        if award['id'] == award_id:
            self.assertEqual(award['complaints'][0]['status'], 'pending')


def cancellation_tender_active_awarded(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.awarded')
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.awarded')
    self.cancel_tender()
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['active'],
            'data.bids[*].status': ['active', 'active', 'active'],
            'data.qualifications[*].status': ['active', 'active', 'active'],
            'data.awards[*].status': ['active', 'active', 'active'],
            'data.agreements[*].status': ['cancelled'],
            'data.complaints[*].status': ['invalid', 'stopped', 'mistaken']
        })


# Cancellation lot
def cancel_lot_active_tendering(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])

    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    lot_id = response.json['data']['lots'][0]['id']
    self.cancel_tender(lot_id=lot_id)
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['cancelled'],
            'data.bids[*].status': None,
            'data.qualifications[*].status': None,
            'data.awards[*].status': None,
            'data.agreements[*].status': None,
            'data.complaints[*].status': ['invalid', 'stopped', 'mistaken']
        })


def cancel_lot_active_pre_qualification(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.pre-qualification')
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.pre-qualification')
    lot_id = response.json['data']['lots'][0]['id']
    self.cancel_tender(lot_id=lot_id)
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['cancelled'],
            'data.bids[*].status': ['invalid.pre-qualification', 'invalid.pre-qualification',
                                    'invalid.pre-qualification'],
            'data.qualifications[*].status': ['cancelled', 'cancelled', 'cancelled'],
            'data.awards[*].status': None,
            'data.agreements[*].status': None,
            'data.complaints[*].status': ['invalid', 'stopped', 'mistaken']
        })


def cancel_lot_active_pre_qualification_stand_still(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.pre-qualification.stand-still')
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.pre-qualification.stand-still')
    lot_id = response.json['data']['lots'][0]['id']
    self.cancel_tender(lot_id=lot_id)
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['cancelled'],
            'data.bids[*].status': ['invalid.pre-qualification', 'invalid.pre-qualification',
                                    'invalid.pre-qualification'],
            'data.qualifications[*].status': ['cancelled', 'cancelled', 'cancelled'],
            'data.awards[*].status': None,
            'data.agreements[*].status': None,
            'data.complaints[*].status': ['invalid', 'stopped', 'mistaken']
        })


def cancel_lot_active_auction(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.auction')
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.auction')
    lot_id = response.json['data']['lots'][0]['id']
    self.cancel_tender(lot_id=lot_id)
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['cancelled'],
            'data.bids[*].status': ['invalid.pre-qualification', 'invalid.pre-qualification',
                                    'invalid.pre-qualification'],
            'data.qualifications[*].status': ['cancelled', 'cancelled', 'cancelled'],
            'data.awards[*].status': None,
            'data.agreements[*].status': None,
            'data.complaints[*].status': ['invalid', 'stopped', 'mistaken']
        })


def cancel_lot_active_qualification(self):
    self.set_status('active.qualification')
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.qualification')
    lot_id = response.json['data']['lots'][0]['id']
    self.cancel_tender(lot_id=lot_id)
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['cancelled'],
            'data.bids[*].status': ['active', 'active', 'active'],
            'data.qualifications[*].status': ['cancelled', 'cancelled', 'cancelled'],
            'data.awards[*].status': ['pending', 'pending', 'pending'],
            'data.agreements[*].status': None,
            'data.complaints[*].status': None
        })


def cancel_lot_active_qualification_stand_still(self):
    self.set_status('active.qualification.stand-still')
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.qualification.stand-still')
    lot_id = response.json['data']['lots'][0]['id']
    self.cancel_tender(lot_id=lot_id)
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['cancelled'],
            'data.bids[*].status': ['active', 'active', 'active'],
            'data.qualifications[*].status': ['cancelled', 'cancelled', 'cancelled'],
            'data.awards[*].status': ['active', 'active', 'active'],
            'data.agreements[*].status': None,
            'data.complaints[*].status': None
        })


def cancel_lot_active_awarded(self):
    self.set_status('active.awarded')
    response = self.get_tender(role='broker')
    self.assertEqual(response.json['data']["status"], 'active.awarded')
    lot_id = response.json['data']['lots'][0]['id']
    self.cancel_tender(lot_id=lot_id)
    assert_statuses(
        self, rules={
            'data.status': 'cancelled',
            'data.lots[*].status': ['cancelled'],
            'data.bids[*].status': ['active', 'active', 'active'],
            'data.qualifications[*].status': ['cancelled', 'cancelled', 'cancelled'],
            'data.awards[*].status': ['active', 'active', 'active'],
            'data.agreements[*].status': ['cancelled'],
            'data.complaints[*].status': None
        })
