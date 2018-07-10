


# TODO Rewrite this test
def not_found(self):
    auth = self.app.authorization
    for doc_resource in ['financial_documents', 'eligibility_documents', 'qualification_documents']:
        self.app.authorization = auth
        response = self.app.post('/tenders/some_id/bids/some_id/{}?acc_token={}'.format(doc_resource, self.bid_token), status=404, upload_files=[
                                ('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post('/tenders/{}/bids/some_id/{}?acc_token={}'.format(self.tender_id, doc_resource, self.bid_token), status=404, upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, self.bid_token), status=404, upload_files=[
                                ('invalid_value', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.get('/tenders/some_id/bids/some_id/{}?acc_token={}'.format(doc_resource, self.bid_token), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/bids/some_id/{}?acc_token={}'.format(self.tender_id, doc_resource, self.bid_token), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.get('/tenders/some_id/bids/some_id/{}/some_id?acc_token={}'.format(doc_resource, self.bid_token), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/bids/some_id/{}/some_id?acc_token={}'.format(self.tender_id, doc_resource, self.bid_token), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.get('/tenders/{}/bids/{}/{}/some_id?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, self.bid_token), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        response = self.app.put('/tenders/some_id/bids/some_id/{}/some_id?acc_token={}'.format(doc_resource, self.bid_token), status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.put('/tenders/{}/bids/some_id/{}/some_id?acc_token={}'.format(self.tender_id, doc_resource, self.bid_token), status=404, upload_files=[
                                ('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.put('/tenders/{}/bids/{}/{}/some_id?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

        self.app.authorization = ('Basic', ('invalid', ''))
        response = self.app.put('/tenders/{}/bids/{}/{}/some_id?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])


# TODO Rewrite this test
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
    self.assertEqual(len(response.json['data']), 2)
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
    self.assertEqual(len(response.json['data']), 2)
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
    self.assertEqual(len(response.json['data']), 2)
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
    self.assertEqual(len(response.json['data']), 2)
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
    self.assertEqual(len(response.json['data']), 2)
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

    # sign contract
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    self.app.authorization = ('Basic', ('token', ''))
    self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract_id, self.tender_token),
                        {"data": {"status": "active"}})
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 2)
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


# TODO Rewrite this test
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

    # get awards
    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.awarded")

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid2_id, doc_resource,  self.bid_token), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document because award of bid is not in pending or active state")

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)

    # sign contract
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    self.app.authorization = ('Basic', ('token', ''))
    self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract_id, self.tender_token),
                        {"data": {"status": "active"}})
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource,  self.bid_token), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) tender status")


# TODO Rewrite this test
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

    # get awards
    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.awarded")

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.put('/tenders/{}/bids/{}/{}/{}'.format(
            self.tender_id, self.bid2_id, doc_resource, doc_id_by_type2[doc_resource]['id']), upload_files=[('file', 'name.doc', 'content4')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document because award of bid is not in pending or active state")

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)

    # sign contract
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    self.app.authorization = ('Basic', ('token', ''))
    self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract_id, self.tender_token),
                        {"data": {"status": "active"}})
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.put('/tenders/{}/bids/{}/{}/{}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]['id']), upload_files=[('file', 'name.doc', 'content4')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")


# TODO Rewrite this test
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


# TODO Rewrite this test
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


# TODO Rewrite this test
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
    # get awards
    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], "active.awarded")
    test_bids_documents_after_auction_resource(self, doc_id_by_type, private_doc_id_by_type, 'active.pre-qualification')
