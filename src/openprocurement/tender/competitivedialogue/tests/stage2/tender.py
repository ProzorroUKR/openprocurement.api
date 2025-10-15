import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2WebTest,
    BaseCompetitiveDialogUAStage2WebTest,
    test_tender_cd_access_token,
    test_tender_cd_author,
    test_tender_cd_lots,
    test_tender_cdeu_stage2_config,
    test_tender_cdeu_stage2_data,
    test_tender_cdua_stage2_config,
    test_tender_cdua_stage2_data,
)
from openprocurement.tender.competitivedialogue.tests.stage2.tender_blanks import (  # CompetitiveDialogStage2EUResourceTest; TenderStage2UAResourceTest; CompetitiveDialogStage2ResourceTest; TenderStage2UAProcessTest
    create_tender,
    create_tender_central,
    create_tender_invalid_config,
    dateModified_tender,
    first_bid_tender,
    get_tender,
    guarantee,
    invalid_procurementMethod,
    invalid_tender_conditions,
    listing,
    listing_changes,
    listing_draft,
    one_invalid_and_1draft_bids_tender,
    one_valid_bid_tender_ua,
    patch_not_author,
    patch_tender_1,
    patch_tender_eu,
    patch_tender_ua,
    tender_Administrator_change,
    tender_features,
    tender_features_invalid,
    tender_funders,
    tender_milestones_not_required,
    tender_not_found,
)
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.openua.tests.tender_blanks import (
    empty_listing as empty_listing_ua,  # TenderStage2UAResourceTest
)


class CompetitiveDialogStage2EUResourceTest(BaseCompetitiveDialogEUStage2WebTest):
    initial_auth = ("Basic", ("token", ""))
    author_data = test_tender_cd_author
    initial_data = test_tender_cdeu_stage2_data
    initial_config = test_tender_cdeu_stage2_config
    test_access_token_data = test_tender_cd_access_token  # TODO: change attribute identifier
    initial_lots = test_tender_cd_lots

    def set_tender_status(self, tender, token, status):
        auth = self.app.authorization
        if status == "draft.stage2":  # sets automatically in state class
            tender_doc = self.mongodb.tenders.get(tender["id"])
            tender_doc["status"] = "draft.stage2"
            self.mongodb.tenders.save(tender_doc)
        if status == "active.tendering":
            add_criteria(self, tender["id"], token)
            self.app.authorization = ("Basic", ("broker", ""))
            response = self.app.patch_json(
                "/tenders/{id}?acc_token={token}".format(id=tender["id"], token=token), {"data": {"status": status}}
            )
            self.app.authorization = auth
            return response

    test_invalid_procurementMethod = snitch(invalid_procurementMethod)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
    test_create_tender = snitch(create_tender)
    test_create_tender_central = snitch(create_tender_central)
    test_get_tender = snitch(get_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_features = snitch(tender_features)
    test_patch_tender = snitch(patch_tender_1)
    test_patch_tender_eu = snitch(patch_tender_eu)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_guarantee = snitch(guarantee)
    test_tender_Administrator_change = snitch(tender_Administrator_change)
    test_patch_not_author = snitch(patch_not_author)
    test_tender_funders = snitch(tender_funders)
    test_tender_milestones_not_required = snitch(tender_milestones_not_required)


class TenderStage2UAResourceTest(BaseCompetitiveDialogUAStage2WebTest):
    initial_data = test_tender_cdua_stage2_data
    initial_config = test_tender_cdua_stage2_config
    test_access_token_data = test_tender_cd_access_token  # TODO: change attribute identifier
    author_data = test_tender_cd_author
    initial_lots = test_tender_cd_lots

    def set_tender_status(self, tender, token, status):
        auth = self.app.authorization
        if status == "draft.stage2":  # sets automatically in state class
            tender_doc = self.mongodb.tenders.get(tender["id"])
            tender_doc["status"] = "draft.stage2"
            self.mongodb.tenders.save(tender_doc)
        if status == "active.tendering":
            add_criteria(self, tender["id"], token)
            self.app.authorization = ("Basic", ("broker", ""))
            response = self.app.patch_json(
                "/tenders/{id}?acc_token={token}".format(id=tender["id"], token=token), {"data": {"status": status}}
            )
            self.app.authorization = auth
            return response

    test_invalid_procurementMethod = snitch(invalid_procurementMethod)
    test_empty_listing = snitch(empty_listing_ua)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
    test_create_tender = snitch(create_tender)
    test_create_tender_central = snitch(create_tender_central)
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
    test_tender_milestones_not_required = snitch(tender_milestones_not_required)


class TenderStage2UAProcessTest(BaseCompetitiveDialogUAStage2WebTest):
    test_tender_data_ua = deepcopy(test_tender_cdua_stage2_data)  # TODO: change attribute identifier
    test_tender_data_ua["minimalStep"] = {"amount": 15, "currency": "UAH"}  # as test tender doesn't have lots
    author_data = test_tender_cd_author  # TODO: change attribute identifier

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_valid_bid_tender_ua = snitch(one_valid_bid_tender_ua)
    test_1invalid_and_1draft_bids_tender = snitch(one_invalid_and_1draft_bids_tender)
    test_first_bid_tender = snitch(first_bid_tender)


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
