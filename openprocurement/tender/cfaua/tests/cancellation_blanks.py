def patch_tender_agreement_cancellation(self):
    self.set_status('active.awarded')
    lots_ids = [i['id'] for i in self.initial_lots]
    cancellations_ids = []
    for lot_id in lots_ids:
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {
                                          'reason': 'cancellation reason',
                                          "cancellationOf": "lot",
                                          "relatedLot": lot_id
                                      }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellations_ids.append(response.json['data']['id'])
    for cancellation_id in cancellations_ids:
        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, self.tender_token),
            {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    agreements = response.json['data']['agreements']
    for agreement in agreements:
        for item in agreement['items']:
            if item['relatedLot'] in lots_ids:
                self.assertEqual(agreement['status'], 'cancelled')
    self.assertEqual(response.json['data']['status'], 'cancelled')
