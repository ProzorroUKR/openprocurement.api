# -*- coding: utf-8 -*-


def create_active_cancellation_on_tender(self):
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', 'reasonType': 'unsuccessful'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')


def create_complaint_on_tender(self, status="draft"):
    response = self.app.post_json('/tenders/{}/complaints'.format(
        self.tender_id), {
        'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.test_author,
                 'status': status}})
    self.assertEqual(response.status, '201 Created')
    return response.json['data']['id']


def get_tender(self):
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    return response


def assert_statuses(self, **kwargs):
    response = get_tender(self)
    if kwargs['tender_st']:
        self.assertEqual(response.json['data']['status'], kwargs['tender_st'])
    else:
        self.assertNotIn('status', response.json['data'])

    if kwargs['lot_st']:
        for lot in response.json['data']['lots']:
            self.assertEqual(lot['status'], kwargs['lot_st'])
    else:
        self.assertNotIn('lots', response.json['data'])

    if kwargs['bids_st']:
        for bid in response.json['data']['bids']:
            self.assertEqual(bid['status'], kwargs['bids_st'])
    else:
        self.assertNotIn('bids', response.json['data'])

    if kwargs['qualifications_st']:
        for qualification in response.json['data']['qualifications']:
            self.assertEqual(qualification['status'], kwargs['qualifications_st'])
    else:
        self.assertNotIn('qualifications', response.json['data'])

    if kwargs['awards_st']:
        for award in response.json['data']['awards']:
            self.assertEqual(award['status'], kwargs['awards_st'])
    else:
        self.assertNotIn('awards', response.json['data'])

    if kwargs['agreements_st']:
        for agreement in response.json['data']['agreements']:
            self.assertEqual(agreement['status'], kwargs['agreements_st'])
    else:
        self.assertNotIn('agreements', response.json['data'])


def add_tender_complaints(self, statuses):
    # for status in ['satisfied', 'stopped', 'declined', 'mistaken', 'invalid']:
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


def assert_complaint_statuses(self, complaint_statuses):
    response = get_tender(self)
    for i in response.json['data']['complaints']:
        self.assertIn(i['status'], complaint_statuses)
        complaint_statuses.remove(i['status'])


def cancellation_tender_active_tendering(self):
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    complaint_id = create_complaint_on_tender(self, 'claim')
    create_active_cancellation_on_tender(self)
    assert_statuses(
        self, tender_st='cancelled', lot_st='active', bids_st=None,
        qualifications_st=None, awards_st=None, agreements_st=None
    )
    # Complaints status
    response = get_tender(self)
    self.assertEqual(response.json['data']['complaints'][0]['status'], 'claim')


def cancellation_tender_active_pre_qualification(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.tendering', 'end')
    self.check_chronograph()
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.pre-qualification')

    create_active_cancellation_on_tender(self)
    assert_statuses(
        self, tender_st='cancelled', lot_st='active', bids_st='invalid.pre-qualification',
        qualifications_st='pending', awards_st=None, agreements_st=None
    )
    # Complaints status
    response = get_tender(self)
    self.assertEqual(response.json['data']['complaints'][0]['status'], 'invalid')


def cancellation_tender_active_pre_qualification_stand_still(self):
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    complaint_id = create_complaint_on_tender(self, 'pending')
    self.set_status('active.tendering', 'end')
    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json('/tenders/{}/complaints/{}'.format(
        self.tender_id, complaint_id), {'data': {'status': 'invalid'}}
    )
    self.assertEqual(response.status, '200 OK')
    self.check_chronograph()
    self.set_status('active.pre-qualification.stand-still')
    response = get_tender(self)
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

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', 'reasonType': 'unsuccessful'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')

    assert_statuses(
        self, tender_st='cancelled', lot_st='active', bids_st='invalid.pre-qualification',
        qualifications_st='active', awards_st=None, agreements_st=None
    )
    response = get_tender(self)
    self.assertEqual(response.json['data']['complaints'][0]['status'], 'invalid')
    for qualification in response.json['data']['qualifications']:
        if qualification['id'] == qualification_id:
            self.assertEqual(qualification['complaints'][0]['status'], 'pending')


def cancellation_tender_active_auction(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.pre-qualification.stand-still')
    response = get_tender(self)
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

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', 'reasonType': 'unsuccessful'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')
    assert_statuses(
        self, tender_st='cancelled', lot_st='active', bids_st='invalid.pre-qualification',
        qualifications_st='active', awards_st=None, agreements_st=None
    )
    assert_complaint_statuses(self, ['invalid', 'stopped', 'mistaken'])
    response = get_tender(self)
    for qualification in response.json['data']['qualifications']:
        if qualification['id'] == qualification_id:
            self.assertEqual(qualification['complaints'][0]['status'], 'pending')


def cancellation_tender_active_qualification(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.qualification')
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.qualification')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', 'reasonType': 'unsuccessful'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')

    assert_statuses(
        self, tender_st='cancelled', lot_st='active', bids_st='active',
        qualifications_st='active', awards_st='pending', agreements_st=None
    )
    assert_complaint_statuses(self, ['invalid', 'stopped', 'mistaken'])


def cancellation_tender_active_qualification_stand_still(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.qualification.stand-still')
    response = get_tender(self)
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
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.qualification.stand-still')
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', 'reasonType': 'unsuccessful'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')

    assert_statuses(
        self, tender_st='cancelled', lot_st='active', bids_st='active',
        qualifications_st='active', awards_st='active', agreements_st=None
    )
    assert_complaint_statuses(self, ['invalid', 'stopped', 'mistaken'])
    response = get_tender(self)
    for award in response.json['data']['awards']:
        if award['id'] == award_id:
            self.assertEqual(award['complaints'][0]['status'], 'pending')


def cancellation_tender_active_awarded(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.awarded')
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.awarded')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', 'reasonType': 'unsuccessful'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')

    assert_statuses(
        self, tender_st='cancelled', lot_st='active', bids_st='active',
        qualifications_st='active', awards_st='active', agreements_st='pending'
    )
    assert_complaint_statuses(self, ['invalid', 'stopped', 'mistaken'])


# Cancellation lot
def cancel_lot_active_tendering(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])

    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    lot_id = response.json['data']['lots'][0]['id']
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', "cancellationOf": "lot", "relatedLot": lot_id}}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')

    assert_statuses(
        self, tender_st='cancelled', lot_st='cancelled', bids_st=None,
        qualifications_st=None, awards_st=None, agreements_st=None
    )
    assert_complaint_statuses(self, ['invalid', 'stopped', 'mistaken'])


def cancel_lot_active_pre_qualification(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.pre-qualification')
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.pre-qualification')
    lot_id = response.json['data']['lots'][0]['id']
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', "cancellationOf": "lot", "relatedLot": lot_id}}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')

    assert_statuses(
        self, tender_st='cancelled', lot_st='cancelled', bids_st='invalid.pre-qualification',
        qualifications_st='cancelled', awards_st=None, agreements_st=None
    )
    # Complaints status
    assert_complaint_statuses(self, ['invalid', 'stopped', 'mistaken'])


def cancel_lot_active_pre_qualification_stand_still(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.pre-qualification.stand-still')
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.pre-qualification.stand-still')
    lot_id = response.json['data']['lots'][0]['id']
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', "cancellationOf": "lot", "relatedLot": lot_id}}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')
    assert_statuses(
        self, tender_st='cancelled', lot_st='cancelled', bids_st='invalid.pre-qualification',
        qualifications_st='cancelled', awards_st=None, agreements_st=None
    )
    # Complaints status
    assert_complaint_statuses(self, ['invalid', 'stopped', 'mistaken'])


def cancel_lot_active_auction(self):
    add_tender_complaints(self, ['invalid', 'stopped', 'mistaken'])
    self.set_status('active.auction')
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.auction')
    lot_id = response.json['data']['lots'][0]['id']
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', "cancellationOf": "lot", "relatedLot": lot_id}}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')
    assert_statuses(
        self, tender_st='cancelled', lot_st='cancelled', bids_st='invalid.pre-qualification',
        qualifications_st='cancelled', awards_st=None, agreements_st=None
    )
    # Complaints status
    assert_complaint_statuses(self, ['invalid', 'stopped', 'mistaken'])


def cancel_lot_active_qualification(self):
    self.set_status('active.qualification')
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.qualification')
    lot_id = response.json['data']['lots'][0]['id']
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', "cancellationOf": "lot", "relatedLot": lot_id}}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')
    assert_statuses(
        self, tender_st='cancelled', lot_st='cancelled', bids_st='active',
        qualifications_st='cancelled', awards_st='pending', agreements_st=None
    )
    # Complaints status
    self.assertNotIn('complaints', response.json['data'])


def cancel_lot_active_qualification_stand_still(self):
    self.set_status('active.qualification.stand-still')
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.qualification.stand-still')
    lot_id = response.json['data']['lots'][0]['id']
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', "cancellationOf": "lot", "relatedLot": lot_id}}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')
    assert_statuses(
        self, tender_st='cancelled', lot_st='cancelled', bids_st='active',
        qualifications_st='cancelled', awards_st='active', agreements_st=None
    )
    # Complaints status
    self.assertNotIn('complaints', response.json['data'])


def cancel_lot_active_awarded(self):
    self.set_status('active.awarded')
    response = get_tender(self)
    self.assertEqual(response.json['data']["status"], 'active.awarded')
    lot_id = response.json['data']['lots'][0]['id']
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', "cancellationOf": "lot", "relatedLot": lot_id}}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'active')
    assert_statuses(
        self, tender_st='cancelled', lot_st='cancelled', bids_st='active',
        qualifications_st='cancelled', awards_st='active', agreements_st='pending'
    )
    # Complaints status
    self.assertNotIn('complaints', response.json['data'])
