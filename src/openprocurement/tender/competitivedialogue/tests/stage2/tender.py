# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import (
    BaseWebTest,
    snitch,
)
from openprocurement.tender.belowthreshold.tests.base import test_organization

from openprocurement.tender.openua.tests.tender_blanks import (
    # TenderStage2UAResourceTest
    empty_listing as empty_listing_ua
)

from openprocurement.tender.competitivedialogue.tests.stage2.tender_blanks import (
    # CompetitiveDialogStage2Test
    simple_add_cd_tender_eu,
    simple_add_cd_tender_ua,
    # CompetitiveDialogStage2EUResourceTest
    create_tender_invalid_eu,
    patch_tender_eu,
    # TenderStage2UAResourceTest
    create_tender_invalid_ua,
    patch_tender_ua,
    # CompetitiveDialogStage2ResourceTest
    listing,
    listing_draft,
    tender_not_found,
    invalid_procurementMethod,
    listing_changes,
    create_tender,
    tender_features_invalid,
    get_tender,
    tender_features,
    patch_tender_1,
    dateModified_tender,
    guarantee,
    tender_Administrator_change,
    patch_not_author,
    tender_funders,
    # TenderStage2UAProcessTest
    invalid_tender_conditions,
    one_valid_bid_tender_ua,
    one_invalid_and_1draft_bids_tender,
    first_bid_tender,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2WebTest,
    BaseCompetitiveDialogUAStage2WebTest,
    test_tender_stage2_data_ua,
    test_tender_stage2_data_eu,
    test_access_token_stage1,
)


class CompetitiveDialogStage2Test(BaseWebTest):
    test_tender_data_eu = test_tender_stage2_data_eu  # TODO: change attribute identifier
    test_tender_data_ua = test_tender_stage2_data_ua  # TODO: change attribute identifier

    test_simple_add_cd_tender_eu = snitch(simple_add_cd_tender_eu)
    test_simple_add_cd_tender_ua = snitch(simple_add_cd_tender_ua)


class CompetitiveDialogStage2EUResourceTest(BaseCompetitiveDialogEUStage2WebTest):

    initial_auth = ('Basic', ('competitive_dialogue', ''))
    author_data = test_organization
    initial_data = test_tender_stage2_data_eu  # TODO: change attribute identifier
    test_tender_data_eu = test_tender_stage2_data_eu  # TODO: change attribute identifier
    test_access_token_data = test_access_token_stage1  # TODO: change attribute identifier

    def set_tender_status(self, tender, token, status):
        auth = self.app.authorization
        if status == 'draft.stage2':
            self.app.authorization = ('Basic', ('competitive_dialogue', ''))
            response = self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=tender['id'],
                                                                                    token=token),
                                           {'data': {'status': status}})
            self.app.authorization = auth
            return response
        if status == 'active.tendering':
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=tender['id'],
                                                                                    token=token),
                                           {'data': {'status': status}})
            self.app.authorization = auth
            return response

    test_invalid_procurementMethod = snitch(invalid_procurementMethod)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_tender_invalid = snitch(create_tender_invalid_eu)

    # def test_create_tender_generated(self):
    #     self.app.authorization = ('Basic', ('competitive_dialogue', ''))
    #     data = test_tender_stage2_data_ua.copy()
    #     # del data['awardPeriod']
    #     data.update({'id': 'hash', 'doc_id': 'hash2', 'tenderID': 'hash3'})
    #     response = self.app.post_json('/tenders', {'data': data})
    #     self.assertEqual(response.status, '201 Created')
    #     self.assertEqual(response.content_type, 'application/json')
    #     self.set_tender_status(response.json['data'], response.json['access']['token'], 'draft.stage2')
    #     response = self.set_tender_status(response.json['data'], response.json['access']['token'], 'active.tendering')
    #
    #     tender = response.json['data']
    #     if 'procurementMethodDetails' in tender:
    #         tender.pop('procurementMethodDetails')
    #     self.assertEqual(set(tender), set([
    #         u'procurementMethodType', u'id', u'dateModified', u'tenderID',
    #         u'status', u'enquiryPeriod', u'tenderPeriod',
    #         u'complaintPeriod', u'minimalStep', u'items', u'value', u'owner',
    #         u'procuringEntity', u'next_check', u'procurementMethod',
    #         u'awardCriteria', u'submissionMethod', u'title', u'title_en', u'date', u'description',
    #         u'lots', u'dialogueID', u'description_en', u'shortlistedFirms']))
    #     self.assertNotEqual(data['id'], tender['id'])
    #     self.assertNotEqual(data['doc_id'], tender['id'])
    #     self.assertNotEqual(data['tenderID'], tender['tenderID'])

    test_create_tender = snitch(create_tender)
    test_get_tender = snitch(get_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_features = snitch(tender_features)
    test_patch_tender = snitch(patch_tender_1)
    test_patch_tender_ua = snitch(patch_tender_eu)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_guarantee = snitch(guarantee)
    test_tender_Administrator_change = snitch(tender_Administrator_change)
    test_patch_not_author = snitch(patch_not_author)
    test_tender_funders = snitch(tender_funders)

    def test_patch_not_author(self):
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_eu})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        owner_token = response.json['access']['token']

        self.set_tender_status(tender, response.json['access']['token'], 'draft.stage2')
        response = self.set_tender_status(tender, response.json['access']['token'], 'active.tendering')

        tender = response.json['data']

        self.app.authorization = ('Basic', ('bot', 'bot'))

        response = self.app.post('/tenders/{}/documents'.format(tender['id']),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(tender['id'], doc_id, owner_token),
                                       {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")


class TenderStage2UAResourceTest(BaseCompetitiveDialogUAStage2WebTest):
    initial_data = test_tender_stage2_data_ua  # TODO: change attribute identifier
    test_tender_data_eu = test_tender_stage2_data_eu  # TODO: change attribute identifier
    test_access_token_data = test_access_token_stage1  # TODO: change attribute identifier
    author_data = test_organization

    def set_tender_status(self, tender, token, status):
        auth = self.app.authorization
        if status == 'draft.stage2':
            self.app.authorization = ('Basic', ('competitive_dialogue', ''))
            response = self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=tender['id'],
                                                                                    token=token),
                                           {'data': {'status': status}})
            self.app.authorization = auth
            return response
        if status == 'active.tendering':
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=tender['id'],
                                                                                    token=token),
                                           {'data': {'status': status}})
            self.app.authorization = auth
            return response

    test_invalid_procurementMethod = snitch(invalid_procurementMethod)
    test_empty_listing = snitch(empty_listing_ua)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_tender_invalid = snitch(create_tender_invalid_ua)
    test_create_tender = snitch(create_tender)
    test_get_tender = snitch(get_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_features = snitch(tender_features)
    test_patch_tender = snitch(patch_tender_1)
    test_patch_tender_ua = snitch(patch_tender_ua)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_guarantee = snitch(guarantee)
    test_tender_Administrator_change = snitch(tender_Administrator_change)
    test_patch_not_author = snitch(patch_not_author)

    def test_patch_not_author(self):
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        response = self.app.post_json('/tenders', {'data': test_tender_stage2_data_ua})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        owner_token = response.json['access']['token']

        self.set_tender_status(tender, response.json['access']['token'], 'draft.stage2')
        response = self.set_tender_status(tender, response.json['access']['token'], 'active.tendering')

        tender = response.json['data']

        self.app.authorization = ('Basic', ('bot', 'bot'))

        response = self.app.post('/tenders/{}/documents'.format(tender['id']),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        self.app.authorization = authorization
        response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(tender['id'], doc_id, owner_token),
                                       {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")


class TenderStage2UAProcessTest(BaseCompetitiveDialogUAStage2WebTest):
    test_tender_data_ua = test_tender_stage2_data_ua  # TODO: change attribute identifier
    author_data = test_organization # TODO: change attribute identifier
    test_invalid_tender_conditions = snitch(invalid_tender_conditions)

    test_one_valid_bid_tender_ua = snitch(one_valid_bid_tender_ua)

    test_1invalid_and_1draft_bids_tender = snitch(one_invalid_and_1draft_bids_tender)

    test_first_bid_tender = snitch(first_bid_tender)

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
