# -*- coding: utf-8 -*-


def post_tender_auction_all_awards_pending(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current ({}) tender status".format(
                         self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    patch_data = {'bids': []}
    for x in range(self.min_bids_number):
        patch_data['bids'].append({
            "id": self.initial_bids[x]['id'],
            "value": {
                "amount": 409 + x * 10,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            }
        })

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']

    for x in range(self.min_bids_number):
        self.assertEqual(tender["bids"][x]['value']['amount'], patch_data["bids"][x]['value']['amount'])
        self.assertEqual(tender["awards"][x]['status'], 'pending')  # all awards are in pending status

    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    awards = response.json['data']

    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, awards[0]['id'], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}})

    # try to switch not all awards qualified
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                   {"data": {"status": 'active.qualification.stand-still'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     u"Can't switch to 'active.qualification.stand-still' while not all awards are qualified")

    for award in awards[1:]:
        response = self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                   {"data": {"status": 'active.qualification.stand-still'}})
    self.assertEqual(response.json['data']['status'], 'active.qualification.stand-still')

    # switch to active.awarded
    self.set_status('active.awarded', {"id": self.tender_id, 'status': 'active.qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], "active.awarded")

    self.assertIn('contracts', response.json['data'])
