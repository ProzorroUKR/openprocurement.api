# -*- coding: utf-8 -*-
from openprocurement.tender.openua.models import Tender
from openprocurement.tender.openua.tests.base import test_tender_data
from openprocurement.tender.core.utils import prepare_award_milestones
from openprocurement.api.utils import get_now
from openprocurement.tender.core.constants import ALP_MILESTONE_REASONS
from mock import Mock, patch
from datetime import timedelta
from copy import deepcopy
import pytest


test_tender_data = deepcopy(test_tender_data)


@pytest.mark.parametrize("tender_status", ("active.qualification", "active.auction"))
@pytest.mark.parametrize("test_data", [
    (
        (1100, 1000, 1200),  # first check: 1 - (500/ MEAN(1000, 1200)) = 54.(54)%   > 40%
        (500, 1000, 1100),  # second check: 1 - (500/1000) = 50%                     > 30%
        (0, 1)  # indexes of milestone reasons
    ),
    (
        (11000, 833, 800),  # first check: 1 - (490/ MEAN(800 + 833)) = 39.98775%    < 40%
        (490, 700, 850),    # second check: 1 - (490/700) = 30%                      = 30%
        (1,)  # indexes of milestone reasons
    ),
    (
        (600, 1000, 1000),   # first check:  1 - (600/ MEAN(1000 + 1000)) = 40%      = 40%
        (600, 857.14, 850),  # second check: 1 - (600/857.14) = 29.99%               < 30%
        (0,)  # indexes of milestone reasons
    ),
    (
        (600, 999.99, 1000),  # first check:  1 - (600/ MEAN(999.99 + 1000)) = 39.99% < 40%
        (600, 857.14, 850),   # second check: 1 - (600/857.14) = 29.99%               < 30%
        tuple(),  # indexes of milestone reasons
    )
])
def test_milestone_data_cases(test_data, tender_status):
    tendering_amounts, auction_amounts, expected_reason_indexes = test_data
    root = Mock(__parent__=None)
    root.request.content_configurator.reverse_awarding_criteria = False
    root.request.content_configurator.awarding_criteria_key = "amount"
    bids = [
        {"id": str(n) * 32, "value": {"amount": amount}}
        for n, amount in enumerate(auction_amounts)
    ]
    tender_patch = {"status": tender_status, "bids": bids}
    if tender_status == "active.qualification":
        tender_patch["revisions"] = [
            {
                "author": "auction",
                "changes": [
                    {"path": "/bids/{}/value/amount".format(n), "value": amount, "op": "replace"}
                    for n, amount in enumerate(tendering_amounts)
                ]
            }
        ]
    elif tender_status == "active.auction":
        root.request.validated = {"tender_src": {"bids": [
            {
                "id": str(n) * 32,
                "value": {"amount": amount}
            }
            for n,  amount in enumerate(tendering_amounts)
        ]}}
    test_tender_data.update(tender_patch)
    tender = Tender(test_tender_data)
    tender.__parent__ = root

    with patch("openprocurement.tender.core.utils.RELEASE_2020_04_19", get_now() - timedelta(seconds=1)):
        milestones = prepare_award_milestones(tender, bids[0], bids)
    if expected_reason_indexes:
        assert len(milestones) == 1
        assert milestones[0]["code"] == "alp"
        assert milestones[0]["description"] == u" / ".join(ALP_MILESTONE_REASONS[i] for i in expected_reason_indexes)


