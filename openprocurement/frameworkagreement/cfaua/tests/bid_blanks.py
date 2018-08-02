# -*- coding: utf-8 -*-
extra = {
    'agreements': [{
        'contracts': [
            {
                'unitPrices': [{
                    'value': {
                        'amount': 0
                    }
                }]
            }
        ] * 3
    }]
}

def get_tender_bidder(self):
    for _ in range(self.min_bids_number-1):
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': [self.author_data], "value": self.test_bids_data[0]['value']}})

    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    bid_token = response.json['access']['token']
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': [self.author_data], "value": self.test_bids_data[0]['value']}})

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't view bid in current (active.tendering) tender status")

    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], bid)

    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    for b in response.json['data']:
        self.assertEqual(set(b.keys()), set(['id', 'status', 'tenderers']))

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()), set(['id', 'status', 'tenderers']))

    # qualify bids
    response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
    self.app.authorization = ('Basic', ('token', ''))
    for qualification in response.json['data']:
        response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(self.tender_id,
                                                                              qualification['id']),
                                       {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                   {"data": {"status": 'active.pre-qualification.stand-still'}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    for b in response.json['data']:
        self.assertEqual(set(b.keys()), set(['id', 'status', 'tenderers']))

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()), set(['id', 'status', 'tenderers']))

    # switch to active.auction
    self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], "active.auction")

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    for b in response.json['data']:
        self.assertEqual(set(b.keys()), set(['id', 'status', 'tenderers']))

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()), set(['id', 'status', 'tenderers']))

    # switch to qualification
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                  {'data': {'bids': auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.qualification")

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    for b in response.json['data']:
        self.assertEqual(set(b.keys()),
                         set([u'date', u'status', u'id', u'value', u'tenderers', 'selfEligible', 'selfQualified']))

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()),
                     set([u'date', u'status', u'id', u'value', u'tenderers', 'selfEligible', 'selfQualified']))

    # get awards
    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

    self.app.authorization = ('Basic', ('token', ''))
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.awarded")

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    for b in response.json['data']:
        self.assertEqual(set(b.keys()),
                         set([u'date', u'status', u'id', u'value', u'tenderers', 'selfEligible', 'selfQualified']))

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()),
                     set([u'date', u'status', u'id', u'value', u'tenderers', 'selfEligible', 'selfQualified']))

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)

    # sign agreement
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']
    self.app.authorization = ('Basic', ('token', ''))
    self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, self.tender_token),
                        {"data": {"status": "active"}})
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    for b in response.json['data']:
        self.assertEqual(set(b.keys()),
                         set([u'date', u'status', u'id', u'value', u'tenderers', 'selfEligible', 'selfQualified']))

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()),
                     set([u'date', u'status', u'id', u'value', u'tenderers', 'selfEligible', 'selfQualified']))


def get_tender_bidder_document(self):

    doc_id_by_type = {}
    # self.app.authorization = ('Basic', ('anon', ''))
    
    def document_is_unaccessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker05', ''))
        response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, self.bid_id, resource), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        doc_id = doc_id_by_type[resource]['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, resource, doc_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.app.authorization = orig_auth

    def document_is_unaccessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, self.tender_token), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        doc_id = doc_id_by_type[resource]['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, doc_id, self.tender_token), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.app.authorization = orig_auth

    def all_documents_are_accessible_for_bid_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker', ''))
        for resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
            response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 2)
            doc1 = response.json['data'][0]
            doc2 = response.json['data'][1]
            self.assertEqual(doc1['title'], 'name_{}.doc'.format(resource[:-1]))
            self.assertEqual(doc2['title'], 'name_{}_private.doc'.format(resource[:-1]))
            self.assertEqual(doc1['confidentiality'], u'public')
            self.assertEqual(doc2['confidentiality'], u'buyerOnly')
            self.assertIn('url', doc1)
            self.assertIn('url', doc2)
            doc_id = doc_id_by_type[resource]['id']
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, doc_id, self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertIn('previousVersions', response.json['data'])
            doc = response.json['data']
            del doc['previousVersions']
            self.assertEqual(doc, doc1)
            doc_id = doc_id_by_type[resource+'private']['id']
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, doc_id, self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertIn('previousVersions', response.json['data'])
            doc = response.json['data']
            del doc['previousVersions']
            self.assertEqual(doc, doc2)
        self.app.authorization = orig_auth

    def documents_are_accessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker', ''))
        token = self.tender_token
        response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 2)
        doc_id = doc_id_by_type[resource]['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, doc_id, token))
        self.assertIn('url', response.json['data'])
        self.assertEqual(response.status, '200 OK')
        doc_id = doc_id_by_type[resource+'private']['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, doc_id, token))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('url', response.json['data'])
        self.app.authorization = orig_auth

    def public_documents_are_accessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker05', ''))

        response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, self.bid_id, resource))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 2)
        self.assertIn(doc_id_by_type[resource]['key'], response.json['data'][0]['url'])
        self.assertNotIn('url', response.json['data'][1])

        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, resource,
                                                                   doc_id_by_type[resource]['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], 'name_{}.doc'.format(resource[:-1]))
        self.assertEqual(response.json['data']['confidentiality'], u'public')
        self.assertEqual(response.json['data']['format'], u'application/msword')
        self.assertEqual(response.json['data']['language'], 'uk')

        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, resource,
                                                                   doc_id_by_type[resource+'private']['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['confidentiality'], u'buyerOnly')
        self.assertNotIn('url', response.json['data'])

        self.app.authorization = orig_auth

    def all_public_documents_are_accessible_for_others():
        for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
            public_documents_are_accessible_for_others(doc_resource)

    # active.tendering
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}

        # upload private document
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}_private.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}_private.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]
        doc_id_by_type[doc_resource+'private'] = {'id': doc_id, 'key': key}
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), { "data": {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }})
        self.assertEqual(response.status, '200 OK')

        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    all_documents_are_accessible_for_bid_owner(doc_resource)

    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    self.assertEqual(set(response.json['data'][0].keys()), set(['id', 'status', 'documents', 'eligibilityDocuments', 'tenderers']))
    self.assertEqual(set(response.json['data'][1].keys()), set(['id', 'status', 'tenderers']))
    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()), set(['id', 'status', 'documents', 'eligibilityDocuments', 'tenderers']))

    for doc_resource in ['documents', 'eligibility_documents']:
        response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, self.bid_id, doc_resource))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 2)
        self.assertIn('url', response.json['data'][0])
        self.assertIn(doc_id_by_type[doc_resource]['key'], response.json['data'][0]['url'])
        self.assertNotIn('url', response.json['data'][1])

    for doc_resource in ['documents', 'eligibility_documents']:
        doc_id = doc_id_by_type[doc_resource]['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], u'name_{}.doc'.format(doc_resource[:-1]))
        self.assertEqual(response.json['data']['confidentiality'], u'public')
        self.assertEqual(response.json['data']['format'], u'application/msword')
        self.assertEqual(response.json['data']['language'], 'uk')

        doc_id = doc_id_by_type[doc_resource+'private']['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], u'name_{}_private.doc'.format(doc_resource[:-1]))
        self.assertEqual(response.json['data']['confidentiality'], u'buyerOnly')
        self.assertEqual(response.json['data']['format'], u'application/msword')
        self.assertEqual(response.json['data']['language'], 'uk')

    for doc_resource in ['financial_documents', 'qualification_documents']:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ['documents', 'eligibility_documents']:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)
    
    # qualify bids
    response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
    self.app.authorization = ('Basic', ('token', ''))
    for qualification in response.json['data']:
        response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(self.tender_id,
                                                                              qualification['id']),
                                       {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"status": 'active.pre-qualification.stand-still'}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    self.assertEqual(set(response.json['data'][0].keys()), set(['id', 'status', 'documents', 'eligibilityDocuments', 'tenderers']))
    self.assertEqual(set(response.json['data'][1].keys()), set(['id', 'status', 'tenderers']))
    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()), set(['id', 'status', 'documents', 'eligibilityDocuments', 'tenderers']))
    response = self.app.get('/tenders/{}/bids/{}/documents'.format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 2)
    self.assertIn(doc_id_by_type['documents']['key'], response.json['data'][0]['url'])
    doc_id = doc_id_by_type['documents']['id']
    response = self.app.get('/tenders/{}/bids/{}/documents/{}'.format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['title'], u'name_document.doc')
    self.assertEqual(response.json['data']['confidentiality'], u'public')
    self.assertEqual(response.json['data']['format'], u'application/msword')
    for doc_resource in ['financial_documents', 'qualification_documents']:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ['documents', 'eligibility_documents']:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)
    
    # switch to active.auction
    self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], "active.auction")

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    self.assertEqual(set(response.json['data'][0].keys()), set(['id', 'status', 'documents', 'eligibilityDocuments', 'tenderers']))
    self.assertEqual(set(response.json['data'][1].keys()), set(['id', 'status', 'tenderers']))
    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()), set(['id', 'status', 'documents', 'eligibilityDocuments', 'tenderers']))
    response = self.app.get('/tenders/{}/bids/{}/documents'.format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 2)
    self.assertIn(doc_id_by_type['documents']['key'], response.json['data'][0]['url'])
    doc_id = doc_id_by_type['documents']['id']
    response = self.app.get('/tenders/{}/bids/{}/documents/{}'.format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['title'], u'name_document.doc')
    self.assertEqual(response.json['data']['confidentiality'], u'public')
    self.assertEqual(response.json['data']['format'], u'application/msword')
    for doc_resource in ['financial_documents', 'qualification_documents']:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ['documents', 'eligibility_documents']:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)
    
    # switch to qualification
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                  {'data': {'bids': auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.qualification")
    
    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    self.assertEqual(set(response.json['data'][0].keys()), set([u'date', u'status', u'id', u'value', u'tenderers', u'documents',
                                                                u'eligibilityDocuments', u'qualificationDocuments', u'financialDocuments',
                                                                u'selfEligible', u'selfQualified']))
    self.assertEqual(set(response.json['data'][1].keys()), set([u'date', u'status', u'id', u'value', u'tenderers',
                                                                u'selfEligible', u'selfQualified']))
    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()), set([u'date', u'status', u'id', u'value', u'tenderers', u'documents',
                                                             u'eligibilityDocuments', u'qualificationDocuments', u'financialDocuments',
                                                             u'selfEligible', u'selfQualified']))

    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()

    # switch to active.awarded
    # fill missing unitPrices.value.amount with zeros
    self.set_status('active.awarded', extra=extra)

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.awarded")

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    self.assertEqual(set(response.json['data'][0].keys()), set([u'date', u'status', u'id', u'value', u'tenderers', u'documents',
                                                                u'eligibilityDocuments', u'qualificationDocuments', u'financialDocuments',
                                                                u'selfEligible', u'selfQualified']))
    self.assertEqual(set(response.json['data'][1].keys()), set([u'date', u'status', u'id', u'value', u'tenderers',
                                                                u'selfEligible', u'selfQualified']))
    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()), set([u'date', u'status', u'id', u'value', u'tenderers', u'documents',
                                                             u'eligibilityDocuments', u'qualificationDocuments', u'financialDocuments',
                                                             u'selfEligible', u'selfQualified']))
    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    
    # sign agreement
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']
    self.app.authorization = ('Basic', ('token', ''))
    self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, self.tender_token),
        {"data": {"status": "active"}}
    )
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), self.min_bids_number)
    self.assertEqual(set(response.json['data'][0].keys()), set([u'date', u'status', u'id', u'value', u'tenderers', u'documents',
                                                                u'eligibilityDocuments', u'qualificationDocuments', u'financialDocuments',
                                                                u'selfEligible', u'selfQualified']))
    self.assertEqual(set(response.json['data'][1].keys()), set([u'date', u'status', u'id', u'value', u'tenderers',
                                                                u'selfEligible', u'selfQualified']))
    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()), set([u'date', u'status', u'id', u'value', u'tenderers', u'documents',
                                                             u'eligibilityDocuments', u'qualificationDocuments', u'financialDocuments',
                                                             u'selfEligible', u'selfQualified']))
    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()


def create_tender_bidder_document(self):
    doc_id_by_type = {}
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])


        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']

        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}


    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id_by_type[doc_resource]['id'], response.json["data"][0]["id"])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/bids/{}/{}?all=true&acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id_by_type[doc_resource]['id'], response.json["data"][0]["id"])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"][0]["title"])

        doc_id = doc_id_by_type[doc_resource]['id']
        key = doc_id_by_type[doc_resource]['key']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}?download=some_id&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, key), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

        if self.docservice:
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}&acc_token={}'.format(
                self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertIn('Expires=', response.location)
        else:
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}&acc_token={}'.format(
                self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 7)
            self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])

    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {'status': 'active.tendering'})
    auth = self.app.authorization
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.app.authorization = auth

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.pre-qualification) tender status")

    # list qualifications
    response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, "200 OK")
    # qualify bids
    for qualification in response.json['data']:
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                           qualification['id'],
                                                                                           self.tender_token),
                                       {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")


    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.pre-qualification.stand-still) tender status")

    # switch to active.auction
    self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], "active.auction")

    self.app.authorization = ('Basic', ('token', ''))
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource,  self.bid_token), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.auction) tender status")

    # switch to qualification
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                  {'data': {'bids': auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.qualification")

    self.app.authorization = ('Basic', ('token', ''))
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name2_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')

    # switch to active.awarded
    # fill missing unitPrices.value.amount with zeros
    self.set_status('active.awarded', extra=extra)

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.awarded")
    
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid2_id, doc_resource,  self.bid_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)

    # sign agreement
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']
    self.app.authorization = ('Basic', ('token', ''))
    self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(
        self.tender_id, agreement_id, self.tender_token), {"data": {"status": "active"}})
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource,  self.bid_token), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) tender status")


def put_tender_bidder_document(self):
    doc_id_by_type = {}
    doc_id_by_type2 = {}
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': response.json["data"]["url"].split('?')[-1].split('=')[-1]}

        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid2_id, doc_resource, self.bid2_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id_by_type2[doc_resource] = {'id': response.json["data"]['id'], 'key': response.json["data"]["url"].split('?')[-1].split('=')[-1]}

        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), status=404,
                                upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?download={}&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token))
        if self.docservice:
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertIn('Expires=', response.location)
        else:
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), 'content3', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?download={}&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token))
        if self.docservice:
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertIn('Expires=', response.location)
        else:
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content3')

    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {'status': 'active.tendering'})
    auth = self.app.authorization
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.app.authorization = auth

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]['id'], self.bid_token), upload_files=[('file', 'name.doc', 'content4')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.pre-qualification) tender status")

    # list qualifications
    response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    # qualify bids
    for qualification in response.json['data']:
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                           qualification['id'],
                                                                                           self.tender_token),
                                       {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]['id'], self.bid_token), upload_files=[('file', 'name.doc', 'content4')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.pre-qualification.stand-still) tender status")

    # switch to active.auction
    self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], "active.auction")

    self.app.authorization = ('Basic', ('broker', ''))
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]['id'], self.bid_token), upload_files=[('file', 'name.doc', 'content4')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.auction) tender status")

    # switch to qualification
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                  {'data': {'bids': auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.qualification")

    self.app.authorization = ('Basic', ('token', ''))
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.put('/tenders/{}/bids/{}/{}/{}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]['id']), upload_files=[('file', 'name.doc', 'content4')])
        self.assertEqual(response.status, '200 OK')

    # switch to active.awarded
    # fill missing unitPrices.value.amount with zeros
    self.set_status('active.awarded', extra=extra)

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.awarded")

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.put('/tenders/{}/bids/{}/{}/{}'.format(
            self.tender_id, self.bid2_id, doc_resource, doc_id_by_type2[doc_resource]['id']), upload_files=[('file', 'name.doc', 'content4')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)

    # sign agreement
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']
    self.app.authorization = ('Basic', ('token', ''))
    self.app.patch_json(
        '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, self.tender_token),
        {"data": {"status": "active"}}
    )
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.put('/tenders/{}/bids/{}/{}/{}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]['id']), upload_files=[('file', 'name.doc', 'content4')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")


def delete_tender_bidder(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': self.test_bids_data[0]['tenderers'], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    bid_token = response.json['access']['token']

    response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['id'], bid['id'])
    self.assertEqual(response.json['data']['status'], 'deleted')
    # deleted bid does not contain bid information
    self.assertFalse('value' in response.json['data'])
    self.assertFalse('tenderers' in response.json['data'])
    self.assertFalse('date' in response.json['data'])

    # try to add documents to bid
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, bid['id'], doc_resource, bid_token),
            upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document to 'deleted' bid")

    revisions = self.db.get(self.tender_id).get('revisions')
    self.assertTrue(any([i for i in revisions[-2][u'changes'] if i['op'] == u'remove' and i['path'] == u'/bids']))
    self.assertTrue(
        any([i for i in revisions[-1][u'changes'] if i['op'] == u'replace' and i['path'] == u'/bids/0/status']))

    response = self.app.delete('/tenders/{}/bids/some_id'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'bid_id'}
    ])

    response = self.app.delete('/tenders/some_id/bids/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    # create new bid
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': self.test_bids_data[0]['tenderers'], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    bid = response.json['data']
    bid_token = response.json['access']['token']

    # update tender. we can set value that is less than a value in bid as
    # they will be invalidated by this request
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data":
                                                                                                              {
                                                                                                                  "value": {
                                                                                                                      'amount': 300.0}}
                                                                                                          })
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["value"]["amount"], 300)

    # check bid 'invalid' status
    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'invalid')

    # try to delete 'invalid' bid
    response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['id'], bid['id'])
    self.assertEqual(response.json['data']['status'], 'deleted')

    for i in range(self.min_bids_number):
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': self.test_bids_data[i]['tenderers'], "value": {"amount": 100+i}}})

    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')
    # qualify bids
    response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
    self.app.authorization = ('Basic', ('token', ''))
    for qualification in response.json['data']:
        response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(
            self.tender_id, qualification['id']), {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

    # switch to active.auction
    self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], "active.auction")

    # switch to qualification
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                  {'data': {'bids': auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.qualification")

    # switch to active.awarded
    # fill missing unitPrices.value.amount with zeros
    self.set_status('active.awarded', extra=extra)

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.awarded")

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)

    # sign agreement
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']
    self.app.authorization = ('Basic', ('token', ''))
    self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(
        self.tender_id, agreement_id, self.tender_token), {"data": {"status": "active"}})
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')

    # finished tender does not show deleted bid info
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']['bids']), self.min_bids_number + 2)
    bid_data = response.json['data']['bids'][1]
    self.assertEqual(bid_data['id'], bid['id'])
    self.assertEqual(bid_data['status'], 'deleted')
    self.assertFalse('value' in bid_data)
    self.assertFalse('tenderers' in bid_data)
    self.assertFalse('date' in bid_data)



def patch_tender_bidder_document(self):
    doc_id_by_type = {}
    doc_id_by_type2 = {}
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}

        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid2_id, doc_resource, self.bid2_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id_by_type2[doc_resource] = {'id': response.json["data"]['id'], 'key': response.json["data"]["url"].split('?')[-1]}

        # upload private document
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}_private.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}_private.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource+'private'] = {'id': doc_id, 'key': key}
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), { "data": {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid2_id, doc_resource, self.bid2_token), upload_files=[('file', 'name_{}_private.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}_private.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type2[doc_resource+'private'] = {'id': doc_id, 'key': key}
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid2_id, doc_resource, doc_id, self.bid2_token), { "data": {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }})
        self.assertEqual(response.status, '200 OK')


def patch_tender_bidder_document_private(self):
    doc_id_by_type = {}
    private_doc_id_by_type = {}
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), { "data": {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('buyerOnly', response.json["data"]["confidentiality"])
        self.assertEqual('Only our company sells badgers with pink hair.', response.json["data"]["confidentialityRationale"])
        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        self.assertEqual('buyerOnly', response.json["data"]["confidentiality"])
        self.assertEqual('Only our company sells badgers with pink hair.', response.json["data"]["confidentialityRationale"])


def download_tender_bidder_document(self):
    doc_id_by_type = {}
    private_doc_id_by_type = {}
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        private_doc_id_by_type[doc_resource] = {'id': response.json["data"]['id'], 'key': response.json["data"]["url"].split('?')[-1]}

        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), { "data": {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }})

        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': response.json["data"]['id'], 'key': response.json["data"]["url"].split('?')[-1]}

        for container in private_doc_id_by_type, doc_id_by_type:
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.bid_token, container[doc_resource]['key']))
            if self.docservice:
                self.assertEqual(response.status, '302 Moved Temporarily')
                self.assertIn('http://localhost/get/', response.location)
                self.assertIn('Signature=', response.location)
                self.assertIn('KeyID=', response.location)
                self.assertIn('Expires=', response.location)
            else:
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.body, 'content')
                self.assertEqual(response.headers['Content-Disposition'],  'attachment; filename=name_{}.doc'.format(doc_resource[:-1]))
                self.assertEqual(response.headers['Content-Type'],  'application/msword; charset=UTF-8')

            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.tender_token, container[doc_resource]['key']), status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

            response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(
                self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], container[doc_resource]['key']), status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

    self.time_shift('active.pre-qualification')
    self.check_chronograph()

    def test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, status):
        for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                    self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.bid_token, container[doc_resource]['key']))
                if self.docservice:
                    self.assertEqual(response.status, '302 Moved Temporarily')
                    self.assertIn('http://localhost/get/', response.location)
                    self.assertIn('Signature=', response.location)
                    self.assertIn('KeyID=', response.location)
                else:
                    self.assertEqual(response.status, '200 OK')
                    self.assertEqual(response.body, 'content')
                    self.assertEqual(response.headers['Content-Disposition'],  'attachment; filename=name_{}.doc'.format(doc_resource[:-1]))
                    self.assertEqual(response.headers['Content-Type'],  'application/msword; charset=UTF-8')

        for doc_resource in ['documents', 'eligibility_documents']:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                    self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.tender_token, container[doc_resource]['key']))
                if self.docservice:
                    self.assertEqual(response.status, '302 Moved Temporarily')
                    self.assertIn('http://localhost/get/', response.location)
                    self.assertIn('Signature=', response.location)
                    self.assertIn('KeyID=', response.location)
                else:
                    self.assertEqual(response.status, '200 OK')

        for doc_resource in ['financial_documents', 'qualification_documents']:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                    self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.tender_token, container[doc_resource]['key']), status=403)
                self.assertEqual(response.status, '403 Forbidden')
                self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current ({}) tender status".format(status))

        # for doc_resource in ['documents', 'eligibility_documents']:
            # for container in private_doc_id_by_type, doc_id_by_type:
                # response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                    # self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.tender_token, container[doc_resource]['key']))
                # self.assertEqual(response.status, '200 OK')

        for doc_resource in ['financial_documents', 'qualification_documents']:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(
                    self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], container[doc_resource]['key']), status=403)
                self.assertEqual(response.status, '403 Forbidden')
                self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current ({}) tender status".format(status))

    test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, 'active.pre-qualification')

    response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    # qualify bids
    for qualification in response.json['data']:
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                           qualification['id'],
                                                                                           self.tender_token),
                                       {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')
    test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, 'active.pre-qualification.stand-still')

    self.time_shift('active.auction')
    self.check_chronograph()
    test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, 'active.auction')

    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']

        # posting auction urls
    response = self.app.patch_json('/tenders/{}/auction'.format(self.tender_id), {
        'data': {
            'auctionUrl': 'https://tender.auction.url',
            'bids': [
                {
                    'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id']),
                    'id': i['id']
                }
                for i in auction_bids_data
            ]
        }
    })
     # posting auction results
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': auction_bids_data}})
    self.assertEqual(response.json['data']['status'], 'active.qualification')

    self.app.authorization = ('Basic', ('broker', ''))
    def test_bids_documents_after_auction_resource(self, doc_id_by_type, private_doc_id_by_type, status):
        for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                    self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.bid_token, container[doc_resource]['key']))
                if self.docservice:
                    self.assertEqual(response.status, '302 Moved Temporarily')
                    self.assertIn('http://localhost/get/', response.location)
                    self.assertIn('Signature=', response.location)
                    self.assertIn('KeyID=', response.location)
                else:
                    self.assertEqual(response.status, '200 OK')
                    self.assertEqual(response.body, 'content')
                    self.assertEqual(response.headers['Content-Disposition'],  'attachment; filename=name_{}.doc'.format(doc_resource[:-1]))
                    self.assertEqual(response.headers['Content-Type'],  'application/msword; charset=UTF-8')

        for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                    self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.tender_token, container[doc_resource]['key']))
                if self.docservice:
                    self.assertEqual(response.status, '302 Moved Temporarily')
                    self.assertIn('http://localhost/get/', response.location)
                    self.assertIn('Signature=', response.location)
                    self.assertIn('KeyID=', response.location)
                else:
                    self.assertEqual(response.status, '200 OK')
                    self.assertEqual(response.body, 'content')
                    self.assertEqual(response.headers['Content-Disposition'],  'attachment; filename=name_{}.doc'.format(doc_resource[:-1]))
                    self.assertEqual(response.headers['Content-Type'],  'application/msword; charset=UTF-8')

        for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]['id'], doc_id_by_type[doc_resource]['key']))
            if self.docservice:
                self.assertEqual(response.status, '302 Moved Temporarily')
                self.assertIn('http://localhost/get/', response.location)
                self.assertIn('Signature=', response.location)
                self.assertIn('KeyID=', response.location)
            else:
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.body, 'content')
                self.assertEqual(response.headers['Content-Disposition'],  'attachment; filename=name_{}.doc'.format(doc_resource[:-1]))
                self.assertEqual(response.headers['Content-Type'],  'application/msword; charset=UTF-8')

            response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(
                self.tender_id, self.bid_id, doc_resource, private_doc_id_by_type[doc_resource]['id'], private_doc_id_by_type[doc_resource]['key']), status=403)
            self.assertEqual(response.status, '403 Forbidden')

    test_bids_documents_after_auction_resource(self, doc_id_by_type, private_doc_id_by_type, 'active.pre-qualification')

    # switch to active.awarded
    # fill missing unitPrices.value.amount with zeros
    self.set_status('active.awarded', extra=extra)

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.awarded")
    test_bids_documents_after_auction_resource(self, doc_id_by_type, private_doc_id_by_type, 'active.pre-qualification')


def create_tender_bidder_document_nopending(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': self.test_bids_data[0]})
    bid = response.json['data']
    token = response.json['access']['token']
    bid_id = bid['id']

    response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
        self.tender_id, bid_id, token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    # qualify bids
    response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
    self.app.authorization = ('Basic', ('token', ''))
    for qualification in response.json['data']:
        response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(
        self.tender_id, qualification['id']), {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"status": 'active.pre-qualification.stand-still'}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

    # switch to active.auction
    self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(
        self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], "active.auction")

    # switch to qualification
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                  {'data': {'bids': auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.qualification")

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, bid_id, doc_id, token), {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.put('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, bid_id, doc_id, token), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
        self.tender_id, bid_id, token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
