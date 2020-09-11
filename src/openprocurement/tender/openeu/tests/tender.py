# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    # TenderProcessTest
    invalid_tender_conditions,
    # TenderResourceTest
    guarantee,
    create_tender_with_inn,
    create_tender_with_inn_before,
    tender_milestones_required,
    patch_tender_lots_none,
    create_tender_central,
    create_tender_central_invalid,
    tender_minimalstep_validation,
    patch_tender_minimalstep_validation,
)

from openprocurement.tender.openuadefense.tests.base import test_bids
from openprocurement.tender.openua.tests.tender import TenderUAResourceTestMixin
from openprocurement.tender.openua.tests.tender_blanks import (
    tender_with_main_procurement_category,
    tender_finance_milestones,
)
from openprocurement.tender.openeu.tests.base import test_tender_data, BaseTenderWebTest, test_lots, test_bids
from openprocurement.tender.openeu.tests.tender_blanks import (
    # TenderProcessTest
    one_bid_tender,
    unsuccessful_after_prequalification_tender,
    one_qualificated_bid_tender,
    multiple_bidders_tender,
    lost_contract_for_active_award,
    # TenderResourceTest
    create_tender_invalid,
    create_tender_generated,
    patch_tender,
    invalid_bid_tender_features,
    invalid_bid_tender_lot,
    # TenderTest
    simple_add_tender,
)


class TenderTest(BaseTenderWebTest):

    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_data

    test_simple_add_tender = snitch(simple_add_tender)


class TenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin, TenderUAResourceTestMixin):

    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_data
    test_lots_data = test_lots
    test_bids_data = test_bids

    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_central = snitch(create_tender_central)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_tender = snitch(patch_tender)
    test_guarantee = snitch(guarantee)
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_create_tender_with_inn_before = snitch(create_tender_with_inn_before)
    test_tender_milestones_required = snitch(tender_milestones_required)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_tender_minimalstep_validation = snitch(tender_minimalstep_validation)
    test_patch_tender_minimalstep_validation = snitch(patch_tender_minimalstep_validation)

    def test_patch_not_author(self):
        response = self.app.post_json("/tenders", {"data": test_tender_data})
        self.assertEqual(response.status, "201 Created")
        tender = response.json["data"]
        owner_token = response.json["access"]["token"]

        authorization = self.app.authorization
        self.app.authorization = ("Basic", ("bot", "bot"))

        response = self.app.post(
            "/tenders/{}/documents".format(tender["id"]), upload_files=[("file", "name.doc", "content")]
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])

        self.app.authorization = authorization
        response = self.app.patch_json(
            "/tenders/{}/documents/{}?acc_token={}".format(tender["id"], doc_id, owner_token),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")


class TenderProcessTest(BaseTenderWebTest):

    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_data
    test_bids_data = test_bids

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_bid_tender = snitch(one_bid_tender)
    test_unsuccessful_after_prequalification_tender = snitch(unsuccessful_after_prequalification_tender)
    test_one_qualificated_bid_tender = snitch(one_qualificated_bid_tender)
    test_multiple_bidders_tender = snitch(multiple_bidders_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderProcessTest))
    suite.addTest(unittest.makeSuite(TenderResourceTest))
    suite.addTest(unittest.makeSuite(TenderTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
