# -*- coding: utf-8 -*-


def post_tender_auction_all_awards_pending(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    patch_data = {'bids': []}
    for x in xrange(self.min_bids_number):
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

    for x in xrange(self.min_bids_number):
        self.assertEqual(tender["bids"][x]['value']['amount'], patch_data["bids"][x]['value']['amount'])
        self.assertEqual(tender["awards"][x]['status'], 'pending')  # all awards are in pending status
