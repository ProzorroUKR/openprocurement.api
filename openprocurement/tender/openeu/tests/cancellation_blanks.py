# -*- coding: utf-8 -*-

# TenderCancellationBidsAvailabilityTest


def bids_on_tender_cancellation_in_tendering(self):
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']
    self.assertNotIn('bids', tender)  # bids not visible for others

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason', "status": "active"}})
    self.assertEqual(response.status, '201 Created')
    cancellation = response.json['data']
    self.assertEqual(cancellation["status"], 'active')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']
    self.assertNotIn('bids', tender)
    self.assertEqual(tender["status"], 'cancelled')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'cancelled')


def bids_on_tender_cancellation_in_pre_qualification(self):
    self._mark_one_bid_deleted()

    # leave one bid invalidated
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {"description": "2 b | !2 b"}})
    for bid_id in self.valid_bids:
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, self.initial_bids_tokens[bid_id]))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'invalid')
    invalid_bid_id = self.valid_bids.pop()
    self.assertEqual(len(self.valid_bids), 2)
    for bid_id in self.valid_bids:
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, self.initial_bids_tokens[bid_id]), {"data": {
            'status': 'pending',
            }})

    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    tender = self._cancel_tender()

    for bid in tender['bids']:
        if bid['id'] in self.valid_bids:
            self.assertEqual(bid["status"], 'invalid.pre-qualification')
            self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
        elif bid['id'] == invalid_bid_id:
            self.assertEqual(bid["status"], 'invalid')
            self.assertEqual(set(bid.keys()), set(['id', 'status']))
        else:
            self.assertEqual(bid["status"], 'deleted')
            self.assertEqual(set(bid.keys()), set(['id', 'status']))

    self._check_visible_fields_for_invalidated_bids()


def bids_on_tender_cancellation_in_pre_qualification_stand_still(self):
    self._mark_one_bid_deleted()

    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    self._qualify_bids_and_switch_to_pre_qualification_stand_still()

    tender = self._cancel_tender()

    self.app.authorization = ('Basic', ('broker', ''))

    for bid in tender['bids']:
        if bid['id'] in self.valid_bids:
            self.assertEqual(bid["status"], 'invalid.pre-qualification')
            self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
        else:
            self.assertEqual(bid["status"], 'deleted')
            self.assertEqual(set(bid.keys()), set(['id', 'status']))

    self._check_visible_fields_for_invalidated_bids()


def bids_on_tender_cancellation_in_auction(self):
    self._mark_one_bid_deleted()

    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    self._qualify_bids_and_switch_to_pre_qualification_stand_still()

    self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.auction')

    tender = self._cancel_tender()

    self.app.authorization = ('Basic', ('broker', ''))
    for bid in tender['bids']:
        if bid['id'] in self.valid_bids:
            self.assertEqual(bid["status"], 'invalid.pre-qualification')
            self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
        else:
            self.assertEqual(bid["status"], 'deleted')
            self.assertEqual(set(bid.keys()), set(['id', 'status']))
            self._all_documents_are_not_accessible(bid['id'])
    self._check_visible_fields_for_invalidated_bids()


def bids_on_tender_cancellation_in_qualification(self):
    self.bid_visible_fields = [
        u'status', u'documents', u'tenderers', u'id', u'selfQualified',
        u'eligibilityDocuments', u'selfEligible', u'value', u'date',
        u'financialDocuments', u'participationUrl', u'qualificationDocuments'
    ]
    deleted_bid_id = self._mark_one_bid_deleted()

    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    self._qualify_bids_and_switch_to_pre_qualification_stand_still(qualify_all=False)

    self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.auction')

    self._set_auction_results()

    tender = self._cancel_tender()

    self.app.authorization = ('Basic', ('broker', ''))
    for bid in tender['bids']:
        if bid['id'] in self.valid_bids:
            self.assertEqual(bid["status"], 'active')
            self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
        elif bid['id'] == deleted_bid_id:
            self.assertEqual(bid["status"], 'deleted')
            self.assertEqual(set(bid.keys()), set(['id', 'status']))
        else:
            self.assertEqual(bid["status"], 'unsuccessful')
            self.assertEqual(set(bid.keys()), set([
                u'documents', u'eligibilityDocuments', u'id', u'status',
                u'selfEligible', u'tenderers', u'selfQualified',
            ]))

    for bid_id, bid_token in self.initial_bids_tokens.items():
        response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid_id))
        bid_data = response.json['data']

        if bid_id in self.valid_bids:
            self.assertEqual(set(bid_data.keys()), set(self.bid_visible_fields))

            for doc_resource in ['documents', 'eligibility_documents', 'financial_documents', 'qualification_documents']:
                self._bid_document_is_accessible(bid_id, doc_resource)
        elif bid_id == deleted_bid_id:
            self._all_documents_are_not_accessible(bid_id)
        else:  # unsuccessful bid
            for doc_resource in ['financial_documents', 'qualification_documents']:
                response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, bid_id, doc_resource), status=403)
                self.assertEqual(response.status, '403 Forbidden')
                self.assertIn("Can\'t view bid documents in current (", response.json['errors'][0]["description"])
                response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, bid_id, doc_resource, self.doc_id_by_type[bid_id + doc_resource]['id']), status=403)
                self.assertEqual(response.status, '403 Forbidden')
                self.assertIn("Can\'t view bid documents in current (", response.json['errors'][0]["description"])
            for doc_resource in ['documents', 'eligibility_documents']:
                self._bid_document_is_accessible(bid_id, doc_resource)


def bids_on_tender_cancellation_in_awarded(self):
    self.bid_visible_fields = [
        u'status', u'documents', u'tenderers', u'id', u'selfQualified',
        u'eligibilityDocuments', u'selfEligible', u'value', u'date',
        u'financialDocuments', u'participationUrl', u'qualificationDocuments'
    ]
    self._mark_one_bid_deleted()

    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    self._qualify_bids_and_switch_to_pre_qualification_stand_still()

    self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.auction')

    self._set_auction_results()

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, "200 OK")

    response = self.app.get('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.awarded')

    tender = self._cancel_tender()

    self.app.authorization = ('Basic', ('broker', ''))
    for bid in tender['bids']:
        if bid['id'] in self.valid_bids:
            self.assertEqual(bid["status"], 'active')
            self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))
        else:
            self.assertEqual(bid["status"], 'deleted')
            self.assertEqual(set(bid.keys()), set(['id', 'status']))

    for bid_id, bid_token in self.initial_bids_tokens.items():

        response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid_id))
        bid_data = response.json['data']
        if bid_id in self.valid_bids:
            self.assertEqual(set(bid_data.keys()), set(self.bid_visible_fields))

            for doc_resource in ['documents', 'eligibility_documents', 'financial_documents', 'qualification_documents']:
                self._bid_document_is_accessible(bid_id, doc_resource)


# TenderAwardsCancellationResourceTest


def cancellation_active_tendering_j708(self):
    bid = self.initial_bids[0].copy()
    value = bid.pop('value')
    bid['lotValues'] = [
        {
            'value': value,
            'relatedLot': self.initial_lots[0]['id'],
        }
    ]
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid})
    self.assertEqual(response.status, '201 Created')
    self.initial_bids_tokens[response.json['data']['id']] = response.json['access']['token']
    self.initial_bids.append(response.json['data'])

    response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, response.json['data']['id'], response.json['access']['token']))
    self.assertEqual(response.status, '200 OK')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'pending',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, response.json['data']['id'], self.tender_token), {'data': {
        'status': 'active',
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid})
    self.assertEqual(response.status, '201 Created')
    self.initial_bids_tokens[response.json['data']['id']] = response.json['access']['token']
    self.initial_bids.append(response.json['data'])

    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')


def cancellation_active_qualification(self):
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        qualification_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification_id, self.tender_token),
                                       {"data": {"status": "active", "qualified": True, "eligible": True}})

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]['id']
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])


def cancellation_unsuccessful_qualification(self):
    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
    qualification_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
    response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification_id, self.tender_token),
                                   {"data": {"status": "unsuccessful", "qualified": True, "eligible": True}})

    response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
    qualification_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
    response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification_id, self.tender_token),
                                   {"data": {"status": "unsuccessful", "qualified": True, "eligible": True}})

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation if all qualifications is unsuccessful")

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
    }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation if all qualifications is unsuccessful")

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[1]['id']
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertEqual(cancellation['status'], 'active')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])


def cancellation_active_award(self):
    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
    self.app.authorization = ('Basic', ('token', ''))
    for qualification in response.json['data']:
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                       {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

    self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], "active.auction")

    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    for lot_id in self.initial_lots:
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                      {'data': {'bids': auction_bids_data}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, 'application/json')
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.qualification")

    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                                   {"data": {"status": "active", "qualified": True, "eligible": True}})

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertEqual(cancellation['status'], 'active')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertEqual(cancellation['status'], 'active')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])


def cancellation_unsuccessful_award(self):
    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
    self.app.authorization = ('Basic', ('token', ''))
    for qualification in response.json['data']:
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                       {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

    self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], "active.auction")

    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    for lot_id in self.initial_lots:
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                      {'data': {'bids': auction_bids_data}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, 'application/json')
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.qualification")

    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                                   {"data": {"status": "unsuccessful"}})

    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                                   {"data": {"status": "unsuccessful"}})

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation if all awards is unsuccessful")

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
    }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation if all awards is unsuccessful")

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[1]['id']
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertEqual(cancellation['status'], 'active')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])
