from iso8601 import parse_date
from openprocurement.api.constants import SANDBOX_MODE
from math import ceil

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


def switch_bid_status_unsuccessul_to_active(self):
    bid_id, bid_token = self.initial_bids_tokens.items()[0]

    response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, 'application/json')
    qualifications = response.json['data']
    self.assertEqual(len(qualifications), 3)
    qualification_id = ""
    for qualification in qualifications:
        status = 'active'
        if qualification['bidID'] == bid_id:
            status = 'unsuccessful'
            qualification_id = qualification["id"]
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                  {"data": {'status': status, "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], status)
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                   {"data": {"status": "active.pre-qualification.stand-still"}})
    self.assertEqual(response.status, "200 OK")
    duration = (parse_date(response.json['data']['qualificationPeriod']['endDate'])
                - parse_date(response.json['data']['date'])).total_seconds()
    if SANDBOX_MODE:
        duration = ceil(duration) * 1440
    duration = duration / 86400 # days float
    self.assertEqual(int(duration), 5)

    # create complaint
    response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, bid_token), {'data': {
        'title': 'complaint title',
        'description': 'complaint description',
        'author': self.initial_bids[0]["tenderers"][0],
        'status': 'pending'
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint['id']), {"data": {
        "status": "accepted"
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "accepted")

    response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(self.tender_id, qualification_id, complaint['id']), {"data": {
        "status": "satisfied"
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "satisfied")

    # Cancell qualification
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification_id, self.tender_token),
                                   {"data": {'status': 'cancelled'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'cancelled')

    new_qualification_id = response.headers['location'].split('/')[-1]
    response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, new_qualification_id, self.tender_token),
                                   {"data": {'status': 'active', "qualified": True, "eligible": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'active')

    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    for b in response.json['data']:
        self.assertEqual(b['status'], 'active')
