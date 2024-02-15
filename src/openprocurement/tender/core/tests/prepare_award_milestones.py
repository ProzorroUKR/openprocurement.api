# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta

import pytest
from mock import Mock, patch

from openprocurement.api.context import set_now, set_request
from openprocurement.api.utils import get_now
from openprocurement.tender.core.constants import ALP_MILESTONE_REASONS
from openprocurement.tender.core.procedure.awarding import TenderStateAwardingMixing
from openprocurement.tender.openua.tests.base import test_tender_openua_data

test_tender_data = deepcopy(test_tender_openua_data)


@pytest.mark.parametrize("tender_status", ("active.qualification", "active.auction"))
@pytest.mark.parametrize(
    "test_data",
    [
        (
            (1100, 1000, 1200),  # first check: 1 - (500/ MEAN(1000, 1200)) = 54.(54)%   > 40%
            (500, 1000, 1100),  # second check: 1 - (500/1000) = 50%                     > 30%
            (0, 1),  # indexes of milestone reasons
        ),
        (
            (11000, 833, 800),  # first check: 1 - (490/ MEAN(800 + 833)) = 39.98775%    < 40%
            (490, 700, 850),  # second check: 1 - (490/700) = 30%                      = 30%
            (1,),  # indexes of milestone reasons
        ),
        (
            (600, 1000, 1000),  # first check:  1 - (600/ MEAN(1000 + 1000)) = 40%      = 40%
            (600, 857.14, 850),  # second check: 1 - (600/857.14) = 29.99%               < 30%
            (0,),  # indexes of milestone reasons
        ),
        (
            (600, 999.99, 1000),  # first check:  1 - (600/ MEAN(999.99 + 1000)) = 39.99% < 40%
            (600, 857.14, 850),  # second check: 1 - (600/857.14) = 29.99%               < 30%
            tuple(),  # indexes of milestone reasons
        ),
        (
            (185000, 182415, 1000),
            (106500, 107000, 850),
            tuple(),  # indexes of milestone reasons
        ),
    ],
)
def test_milestone_data_cases(test_data, tender_status):
    tendering_amounts, auction_amounts, expected_reason_indexes = test_data
    request = Mock(validated={})
    set_request(request)
    set_now()
    bids = [
        {"id": str(n) * 32, "value": {"amount": amount}, "status": "active"} for n, amount in enumerate(auction_amounts)
    ]
    tender_patch = {"status": tender_status, "bids": bids}
    if tender_status == "active.qualification":
        tender_patch["revisions"] = [
            {
                "author": "auction",
                "changes": [
                    {"path": "/bids/{}/value/amount".format(n), "value": amount, "op": "replace"}
                    for n, amount in enumerate(tendering_amounts)
                ],
                "date": get_now().isoformat(),
            }
        ]
    request.validated["tender_src"] = {
        "bids": [
            {
                "id": str(n) * 32,
                "value": {"amount": amount},
                "status": "active",
                "tenderers": [{"identifier": {"id": "00000000"}}],
                "date": "2019-01-01T00:00:00.000000+02:00",
            }
            for n, amount in enumerate(tendering_amounts)
        ]
    }
    test_tender_openua_data.update(tender_patch)
    request.validated["tender"] = test_tender_openua_data

    milestones = TenderStateAwardingMixing().prepare_award_milestones(test_tender_openua_data, bids[0], bids)
    if expected_reason_indexes:
        assert len(milestones) == 1
        assert milestones[0]["code"] == "alp"
        assert milestones[0]["description"] == " / ".join(ALP_MILESTONE_REASONS[i] for i in expected_reason_indexes)
