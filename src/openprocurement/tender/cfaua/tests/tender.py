import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    create_tender_central,
    create_tender_central_invalid,
    create_tender_with_earlier_non_required_unit,
    create_tender_with_inn,
    guarantee,
    invalid_tender_conditions,
    patch_not_author,
    patch_tender_lots_none,
    tender_financing_milestones,
    tender_milestones_required,
)
from openprocurement.tender.cfaua.constants import MIN_BIDS_NUMBER
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    BaseTenderWebTest,
    test_tender_cfaua_bids_with_lotvalues,
    test_tender_cfaua_lots_with_ids,
    test_tender_cfaua_with_lots_data,
)
from openprocurement.tender.cfaua.tests.tender_blanks import (
    active_pre_qualification_to_act_qualification_st,
    active_qualification_to_act_pre_qualification_st,
    agreement_duration_period,
    awards_to_bids_number,
    create_tender_generated,
    create_tender_invalid,
    create_tender_invalid_config,
    create_tender_with_required_unit,
    extract_tender_credentials,
    invalid_bid_tender_features,
    invalid_bid_tender_lot,
    one_bid_tender,
    one_qualificated_bid_tender,
    patch_max_awards,
    patch_tender,
    patch_tender_active_qualification_2_active_qualification_stand_still,
    patch_tender_period,
    patch_unitprice_with_features,
    switch_tender_to_active_awarded,
    tender_contract_period,
    tender_features_invalid,
    tender_milestones_sequence_number,
    tender_with_main_procurement_category,
    unsuccessful_after_prequalification_tender,
)
from openprocurement.tender.competitivedialogue.tests.stage1.tender_blanks import (
    tender_delivery_milestones,
)
from openprocurement.tender.open.tests.tender_blanks import tender_finance_milestones
from openprocurement.tender.openua.tests.tender_blanks import empty_listing


class CFAUATenderTest(BaseTenderWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = deepcopy(test_tender_cfaua_with_lots_data)
    initial_lots = deepcopy(test_tender_cfaua_lots_with_ids)

    test_agreement_duration_period = snitch(agreement_duration_period)


class TenderCheckStatusTest(BaseTenderContentWebTest):
    BaseTenderContentWebTest.backup_pure_data()

    test_active_qualification_to_act_pre_qualification_st = snitch(active_qualification_to_act_pre_qualification_st)
    test_active_pre_qualification_to_act_qualification_st = snitch(active_pre_qualification_to_act_qualification_st)


class TenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = deepcopy(test_tender_cfaua_with_lots_data)
    initial_lots = deepcopy(test_tender_cfaua_lots_with_ids)
    initial_bids = deepcopy(test_tender_cfaua_bids_with_lotvalues)
    test_lots_data = test_tender_cfaua_lots_with_ids
    min_bids_number = MIN_BIDS_NUMBER

    test_empty_listing = snitch(empty_listing)
    # test_tender_fields = snitch(tender_fields)  added new field need to copy and fix this test
    test_patch_tender_period = snitch(patch_tender_period)
    test_tender_contract_period = snitch(tender_contract_period)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
    test_create_tender_central = snitch(create_tender_central)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_tender = snitch(patch_tender)
    test_guarantee = snitch(guarantee)
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)
    test_patch_max_awards = snitch(patch_max_awards)
    test_awards_to_bids_number = snitch(awards_to_bids_number)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_patch_unitprice_with_features = snitch(patch_unitprice_with_features)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_tender_milestones_required = snitch(tender_milestones_required)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_create_cfaua_tender_with_earlier_non_required_unit = snitch(create_tender_with_earlier_non_required_unit)
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)
    test_patch_not_author = snitch(patch_not_author)
    test_tender_delivery_milestones = snitch(tender_delivery_milestones)
    test_tender_financing_milestones = snitch(tender_financing_milestones)
    test_tender_milestones_sequence_number = snitch(tender_milestones_sequence_number)


class TenderProcessTest(BaseTenderWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = deepcopy(test_tender_cfaua_with_lots_data)
    initial_lots = deepcopy(test_tender_cfaua_lots_with_ids)
    initial_bids = deepcopy(test_tender_cfaua_bids_with_lotvalues)

    test_extract_tender_credentials = snitch(extract_tender_credentials)
    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_bid_tender = snitch(one_bid_tender)
    test_unsuccessful_after_prequalification_tender = snitch(unsuccessful_after_prequalification_tender)
    test_one_qualificated_bid_tender = snitch(one_qualificated_bid_tender)

    # test_multiple_bidders_tender = snitch(multiple_bidders_tender)    TODO REWRITE TEST
    # test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)   TODO REWRITE TEST


class TenderPendingAwardsResourceTest(BaseTenderContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = deepcopy(test_tender_cfaua_bids_with_lotvalues)

    def setUp(self):
        # Fix for method create_tender in tender.core and bid.value will be deleted after
        # super(TenderPendingAwardsResourceTest, self).setUp()
        for bid in self.initial_bids:
            bid["value"] = bid["lotValues"][0]["value"]

        super().setUp()
        # switch to active.pre-qualification
        self.set_status("active.pre-qualification")
        response = self.check_chronograph()
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
        for qualific in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualific["id"], self.tender_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")

        self.set_status("active.auction")

        patch_data = {"bids": []}
        for x in range(self.min_bids_number):
            patch_data["bids"].append(
                {
                    "id": self.initial_bids[x]["id"],
                    "lotValues": [
                        {
                            "value": {"amount": 409 + x * 10, "currency": "UAH", "valueAddedTaxIncluded": True},
                            "relatedLot": self.initial_lots[0]["id"],
                        }
                    ],
                }
            )

        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.post_json(
            "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]), {"data": patch_data}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]

        for x in range(self.min_bids_number):
            self.assertEqual(
                tender["bids"][x]["lotValues"][0]["value"]["amount"],
                patch_data["bids"][x]["lotValues"][0]["value"]["amount"],
            )
            self.assertEqual(tender["awards"][x]["status"], "pending")  # all awards are in pending status

    test_patch_tender_active_qualification_2_active_qualification_stand_still = snitch(
        patch_tender_active_qualification_2_active_qualification_stand_still
    )
    test_switch_tender_to_active_awarded = snitch(switch_tender_to_active_awarded)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderProcessTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderPendingAwardsResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
