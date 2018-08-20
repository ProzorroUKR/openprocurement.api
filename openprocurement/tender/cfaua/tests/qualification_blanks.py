def create_tender_lot_qualification_complaint(self):
    response = self.app.post_json(
        '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
            self.tender_id,
            self.qualification_id,
            self.initial_bids_tokens.values()[0]
        ), {
            'data': {
                'title': 'complaint title',
                'description': 'complaint description',
                'author': self.initial_bids[0]["tenderers"][0],
                'status': 'pending'
            }
        }
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']
    self.assertEqual(complaint['author']['name'], self.initial_bids[0]["tenderers"][0]['name'])
    self.assertIn('id', complaint)
    self.assertIn(complaint['id'], response.headers['Location'])

    self.cancel_tender()

    response = self.app.post_json(
        '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
            self.tender_id,
            self.qualification_id,
            self.initial_bids_tokens.values()[0]
        ),{
            'data':
                {
                    'title': 'complaint title',
                    'description': 'complaint description',
                    'author': self.initial_bids[0]["tenderers"][0]
                }
        }, status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add complaint in current (cancelled) tender status")




def create_tender_qualification_complaint(self):
    response = self.app.post_json(
        '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
            self.tender_id,
            self.qualification_id,
            self.initial_bids_tokens.values()[0]
        ),
        {'data':
            {
                'title': 'complaint title',
                'description': 'complaint description',
                'author': self.initial_bids[0]["tenderers"][0],
                'status': 'pending'
            }
        }
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']
    self.assertEqual(complaint['author']['name'], self.initial_bids[0]["tenderers"][0]['name'])
    self.assertIn('id', complaint)
    self.assertIn(complaint['id'], response.headers['Location'])

    self.cancel_tender()

    response = self.app.post_json(
        '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
            self.tender_id,
            self.qualification_id,
            self.initial_bids_tokens.values()[0]
        ),
        {
            'data':
                {
                    'title': 'complaint title',
                    'description': 'complaint description',
                    'author': self.initial_bids[0]["tenderers"][0]
                }
        },
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add complaint in current (cancelled) tender status")