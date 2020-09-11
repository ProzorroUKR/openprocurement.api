# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.pricequotation.adapters import\
    PQTenderConfigurator as TenderBelowThersholdConfigurator
from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_bids,
    test_organization,
)
from openprocurement.tender.pricequotation.tests.award_blanks import (
    check_tender_award,
    create_tender_award_invalid,
    check_tender_award_disqualification,
    create_tender_award,
    patch_tender_award,
    tender_award_transitions,
    check_tender_award_cancellation
)
from openprocurement.tender.belowthreshold.tests.award import (
    TenderAwardDocumentResourceTestMixin,
    TenderAwardResourceTestMixin
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    get_tender_award,
    create_tender_award_with_scale_not_required,
    create_tender_award_no_scale,
    create_tender_award_no_scale_invalid,
    patch_tender_award_Administrator_change,
    create_tender_award_no_scale_invalid,
)

class TenderAwardResourceTestMixin(object):
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)
    test_get_tender_award = snitch(get_tender_award)


class TenderAwardResourceTest(TenderContentWebTest, TenderAwardResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids
    reverse = False
    maxAwards = 1
    # init_awards = False

    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)
    test_tender_award_transitions = snitch(tender_award_transitions)
    test_check_tender_award = snitch(check_tender_award)
    test_check_tender_award_disqualification = snitch(check_tender_award_disqualification)
    test_check_tender_award_cancellation = snitch(check_tender_award_cancellation)


class TenderAwardResourceScaleTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids
    reverse = False

    test_create_tender_award_no_scale = snitch(create_tender_award_no_scale)
    test_create_tender_award_no_scale_invalid = snitch(
        create_tender_award_no_scale_invalid
    )
    test_create_tender_award_with_scale_not_required = snitch(
        create_tender_award_with_scale_not_required
    )


class TenderAwardDocumentResourceTest(TenderContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardDocumentResourceTest, self).setUp()
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.awards_ids = [award["id"] for award in response.json["data"]]

    @property
    def award_id(self):
        data = self.db.get(self.tender_id)
        return data['awards'][-1]['id'] if data.get('awards') else None


class TenderAwardDocumentWithDSResourceTest(TenderAwardDocumentResourceTest):
    docservice = True


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardResourceScaleTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
