# -*- coding: utf-8 -*-


def two_lot_3bid_3com_3win(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # create tender
    response = self.app.post_json('/tenders', {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': self.test_lots_data[0]})
        self.assertEqual(response.status, '201 Created')
        lots.append(response.json['data']['id'])
    self.initial_lots = lots
    # add item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [self.initial_data['items'][0] for i in lots]}})
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': i} for i in lots]}})
    self.assertEqual(response.status, '200 OK')
    # create bids
    for x in range(self.min_bids_number):
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [
                                              {"value": self.test_bids_data[0]['value'], 'relatedLot': lot_id}
                                              for lot_id in lots
                                          ]}})

    # switch to active.pre-qualification
    self.time_shift('active.pre-qualification')
    self.check_chronograph()
    response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, 'application/json')
    qualifications = response.json['data']
    self.assertEqual(len(qualifications), self.min_bids_number * 2)

    for qualification in qualifications:
        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], owner_token),
            {"data": {'status': 'active', "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"status": "active.pre-qualification.stand-still"}})
    self.assertEqual(response.status, "200 OK")
    # switch to active.auction
    self.time_shift('active.auction')
    self.check_chronograph()
    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(tender_id))
    auction_bids_data = response.json['data']['bids']
    for lot_id in lots:
        # posting auction urls
        response = self.app.patch_json('/tenders/{}/auction/{}'.format(tender_id, lot_id), {
            'data': {
                'lots': [
                    {
                        'id': i['id'],
                        'auctionUrl': 'https://tender.auction.url'
                    }
                    for i in response.json['data']['lots']
                ],
                'bids': [
                    {
                        'id': i['id'],
                        'lotValues': [
                            {
                                'relatedLot': j['relatedLot'],
                                'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                            }
                            for j in i['lotValues']
                        ],
                    }
                    for i in auction_bids_data
                ]
            }
        })
        # posting auction results
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.post_json('/tenders/{}/auction/{}'.format(tender_id, lot_id),
                                      {'data': {'bids': auction_bids_data}})
    # for first lot
    lot_id = lots[0]
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    # get agreement id
    response = self.app.get('/tenders/{}'.format(tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']
    # after stand slill period
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # sign agreement
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(tender_id, agreement_id, owner_token),
                        {"data": {"status": "active"}})
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
    # set award as unsuccessful
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                        {"data": {"status": "unsuccessful"}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    # get agreement id
    response = self.app.get('/tenders/{}'.format(tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']
    # after stand slill period
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # sign agreement
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(tender_id, agreement_id, owner_token),
                        {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertTrue(all([i['status'] == 'complete' for i in response.json['data']['lots']]))
    self.assertEqual(response.json['data']['status'], 'complete')


def one_lot_2bid(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # create tender
    response = self.app.post_json('/tenders', {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # add lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                  {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    lot_id = response.json['data']['id']
    self.initial_lots = [response.json['data']]
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '200 OK')
    # create bids
    for x in range(self.min_bids_number):
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': self.test_bids_data[x]["tenderers"], 'lotValues': [
                                              {"value": self.test_bids_data[x]['value'], 'relatedLot': lot_id}]}})
        if x == 0:
            bid_id = response.json['data']['id']
            bid_token = response.json['access']['token']

    # switch to active.auction
    self.time_shift('active.pre-qualification')
    self.check_chronograph()

    response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, 'application/json')
    qualifications = response.json['data']
    for qualification in qualifications:
        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], owner_token),
            {"data": {'status': 'active', "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

    response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
    self.assertEqual(response.status, '200 OK')

    for bid in response.json['data']['bids']:
        self.assertEqual(bid['status'], 'active')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"status": "active.pre-qualification.stand-still"}})
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()

    response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.status, "200 OK")

    self.time_shift('active.auction')

    self.check_chronograph()

    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(tender_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction urls
    response = self.app.patch_json('/tenders/{}/auction/{}'.format(tender_id, lot_id), {
        'data': {
            'lots': [
                {
                    'id': i['id'],
                    'auctionUrl': 'https://tender.auction.url'
                }
                for i in response.json['data']['lots']
            ],
            'bids': [
                {
                    'id': i['id'],
                    'lotValues': [
                        {
                            'relatedLot': j['relatedLot'],
                            'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                        }
                        for j in i['lotValues']
                    ],
                }
                for i in auction_bids_data
            ]
        }
    })
    # view bid participationUrl
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token))
    self.assertEqual(response.json['data']['lotValues'][0]['participationUrl'],
                     'https://tender.auction.url/for_bid/{}'.format(bid_id))
    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction/{}'.format(tender_id, lot_id),
                                  {'data': {'bids': auction_bids_data}})
    # # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as active
    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}}
    )
    # get agreement id
    response = self.app.get('/tenders/{}'.format(tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']
    # after stand slill period

    self.time_shift('complete')
    self.check_chronograph()

    # # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # # sign agreement
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(tender_id, agreement_id, owner_token), {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']["lots"][0]['status'], 'complete')
    self.assertEqual(response.json['data']['status'], 'complete')


def one_lot_3bid_1del(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # create tender
    response = self.app.post_json('/tenders', {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # add lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                  {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    lot_id = response.json['data']['id']
    self.initial_lots = [response.json['data']]
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '200 OK')
    # create bids
    self.app.authorization = ('Basic', ('broker', ''))
    bids = []
    for i in range(self.min_bids_number + 1):
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': self.test_bids_data[0]["tenderers"], 'lotValues': [
                                              {"value": self.test_bids_data[0]['value'], 'relatedLot': lot_id}]}})
        bids.append({response.json['data']['id']: response.json['access']['token']})

    response = self.app.delete(
        '/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bids[2].keys()[0], bids[2].values()[0]))
    self.assertEqual(response.status, '200 OK')
    # switch to active.auction
    self.time_shift('active.pre-qualification')
    self.check_chronograph()

    response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, 'application/json')
    qualifications = response.json['data']

    for qualification in qualifications:
        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], owner_token),
            {"data": {'status': 'active', "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"status": "active.pre-qualification.stand-still"}})
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()

    response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.status, "200 OK")

    response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, 'application/json')
    qualifications = response.json['data']

    self.time_shift('active.auction')

    self.check_chronograph()
    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(tender_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction urls
    data = {
        'data': {
            'lots': [
                {
                    'id': i['id'],
                    'auctionUrl': 'https://tender.auction.url'
                }
                for i in response.json['data']['lots']
            ],
            'bids': list(auction_bids_data)
        }
    }

    for bid_index, bid in enumerate(auction_bids_data):
        if bid.get('status', 'active') == 'active':
            for lot_index, lot_bid in enumerate(bid['lotValues']):
                if lot_bid['relatedLot'] == lot_id and lot_bid.get('status', 'active') == 'active':
                    data['data']['bids'][bid_index]['lotValues'][lot_index][
                        'participationUrl'] = 'https://tender.auction.url/for_bid/{}'.format(bid['id'])
                    break

    response = self.app.patch_json('/tenders/{}/auction/{}'.format(tender_id, lot_id), data)
    # view bid participationUrl
    self.app.authorization = ('Basic', ('broker', ''))
    bid_id = bids[0].keys()[0]
    bid_token = bids[0].values()[0]
    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token))
    self.assertEqual(response.json['data']['lotValues'][0]['participationUrl'],
                     'https://tender.auction.url/for_bid/{}'.format(bid_id))

    bid_id = bids[2].keys()[0]
    bid_token = bids[2].values()[0]
    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token))
    self.assertEqual(response.json['data']['status'], 'deleted')

    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction/{}'.format(tender_id, lot_id),
                                  {'data': {'bids': auction_bids_data}})
    # # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
    # get agreement id
    response = self.app.get('/tenders/{}'.format(tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']
    # after stand slill period

    self.time_shift('complete')
    self.check_chronograph()

    # # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # # sign agreement
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(tender_id, agreement_id, owner_token),
                        {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']["lots"][0]['status'], 'complete')
    self.assertEqual(response.json['data']['status'], 'complete')


def one_lot_3bid_1un(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # create tender
    response = self.app.post_json('/tenders', {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # add lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                  {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    lot_id = response.json['data']['id']
    self.initial_lots = [response.json['data']]
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '200 OK')
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    bids = []
    for i in range(self.min_bids_number + 1):
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': self.test_bids_data[0]["tenderers"], 'lotValues': [
                                              {"value": self.test_bids_data[0]['value'], 'relatedLot': lot_id}]}})
        bids.append({response.json['data']['id']: response.json['access']['token']})

    # switch to active.auction
    self.time_shift('active.pre-qualification')
    self.check_chronograph()

    response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, 'application/json')
    qualifications = response.json['data']
    for qualification in qualifications:
        if qualification['bidID'] == bids[2].keys()[0]:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], owner_token),
                {"data": {'status': 'unsuccessful'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'unsuccessful')
        else:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], owner_token),
                {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"status": "active.pre-qualification.stand-still"}})
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()

    response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.status, "200 OK")

    response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, 'application/json')
    qualifications = response.json['data']

    self.time_shift('active.auction')

    self.check_chronograph()
    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(tender_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction urls
    data = {
        'data': {
            'lots': [
                {
                    'id': i['id'],
                    'auctionUrl': 'https://tender.auction.url'
                }
                for i in response.json['data']['lots']
            ],
            'bids': list(auction_bids_data)
        }
    }

    for bid_index, bid in enumerate(auction_bids_data):
        if bid.get('status', 'active') == 'active':
            for lot_index, lot_bid in enumerate(bid['lotValues']):
                if lot_bid['relatedLot'] == lot_id and lot_bid.get('status', 'active') == 'active':
                    data['data']['bids'][bid_index]['lotValues'][lot_index][
                        'participationUrl'] = 'https://tender.auction.url/for_bid/{}'.format(bid['id'])
                    break

    response = self.app.patch_json('/tenders/{}/auction/{}'.format(tender_id, lot_id), data)
    # view bid participationUrl
    self.app.authorization = ('Basic', ('broker', ''))
    bid_id = bids[0].keys()[0]
    bid_token = bids[0].values()[0]
    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token))
    self.assertEqual(response.json['data']['lotValues'][0]['participationUrl'],
                     'https://tender.auction.url/for_bid/{}'.format(bid_id))

    bid_id = bids[2].keys()[0]
    bid_token = bids[2].values()[0]
    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token))
    self.assertNotIn('lotValues', response.json['data'])

    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction/{}'.format(tender_id, lot_id),
                                  {'data': {'bids': auction_bids_data}})
    # # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
    # get agreement id
    response = self.app.get('/tenders/{}'.format(tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']
    # after stand slill period

    self.time_shift('complete')
    self.check_chronograph()

    # # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # # sign agreement
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(tender_id, agreement_id, owner_token),
                        {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']["lots"][0]['status'], 'complete')
    self.assertEqual(response.json['data']['status'], 'complete')


def two_lot_3bid_1win_bug(self):
    """
    ref: http://prozorro.worksection.ua/project/141436/3931481/#com9856686
    """
    self.app.authorization = ('Basic', ('broker', ''))
    # create tender
    response = self.app.post_json('/tenders', {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': self.test_lots_data[0]})
        self.assertEqual(response.status, '201 Created')
        lots.append(response.json['data']['id'])
    self.initial_lots = lots
    # add item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [self.initial_data['items'][0] for i in lots]}})
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': i} for i in lots]}})
    self.assertEqual(response.status, '200 OK')
    # create bids
    self.app.authorization = ('Basic', ('broker', ''))
    for x in range(self.min_bids_number):
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': self.test_bids_data[x]['tenderers'], 'lotValues': [
                                              {"value": self.test_bids_data[x]['value'], 'relatedLot': lot_id}
                                              for lot_id in lots
                                          ]}})

    # create last bid
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': self.test_bids_data[self.min_bids_number - 1]['tenderers'],
                                            'lotValues': [
                                                {"value": self.test_bids_data[self.min_bids_number - 1]['value'],
                                                 'relatedLot': lot_id}
                                                for lot_id in lots
                                            ]}})
    bid_id = response.json['data']['id']
    # switch to active.pre-qualification
    self.time_shift('active.pre-qualification')
    self.check_chronograph()
    response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, 'application/json')
    qualifications = response.json['data']
    self.assertEqual(len(qualifications), (self.min_bids_number + 1) * 2)

    for qualification in qualifications:
        if lots[1] == qualification['lotID'] and bid_id == qualification['bidID']:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], owner_token),
                {"data": {'status': 'unsuccessful'}})
        else:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], owner_token),
                {"data": {'status': 'active', "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        if lots[1] == qualification['lotID'] and bid_id == qualification['bidID']:
            self.assertEqual(response.json['data']['status'], 'unsuccessful')
        else:
            self.assertEqual(response.json['data']['status'], 'active')
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"status": "active.pre-qualification.stand-still"}})
    self.assertEqual(response.status, "200 OK")
    # switch to active.auction
    self.time_shift('active.auction')
    self.check_chronograph()

    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(tender_id))
    auction_bids_data = response.json['data']['bids']
    for lot_id in lots:
        # posting auction urls
        response = self.app.patch_json('/tenders/{}/auction/{}'.format(tender_id, lot_id), {
            'data': {
                'lots': [
                    {
                        'id': i['id'],
                        'auctionUrl': 'https://tender.auction.url'
                    }
                    for i in response.json['data']['lots']
                ],
                'bids': [
                    {
                        'id': i['id'],
                        'lotValues': [
                            {
                                'relatedLot': j['relatedLot'],
                                'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                            }
                            for j in i['lotValues']
                        ],
                    }
                    for i in auction_bids_data
                ]
            }
        })
        # posting auction results
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.post_json('/tenders/{}/auction/{}'.format(tender_id, lot_id),
                                      {'data': {'bids': auction_bids_data}})
    # for first lot
    lot_id = lots[0]
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
    # get agreement id
    response = self.app.get('/tenders/{}'.format(tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']
    # after stand slill period
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # sign agreement
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(tender_id, agreement_id, owner_token),
                        {"data": {"status": "active"}})
    # for second lot
    lot_id = lots[1]

    for x in range(self.min_bids_number):
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
        # set award as unsuccessful
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                            {"data": {"status": "unsuccessful"}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    self.assertEqual([i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id], [])
    # after stand slill period
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # ping by chronograph
    self.check_chronograph()
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(set([i['status'] for i in response.json['data']['lots']]), set(['complete', 'unsuccessful']))
    self.assertEqual(response.json['data']['status'], 'complete')
