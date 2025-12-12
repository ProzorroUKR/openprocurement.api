from datetime import timedelta
from unittest.mock import Mock, patch

from openprocurement.api.tests.mock import ContextDecorator, patch_multiple
from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.tests.data import (
    test_bid_pq_product,
    test_tender_pq_category,
    test_tender_pq_short_profile,
)

get_tender_profile_targets = [
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_profile",
    "openprocurement.tender.core.procedure.criteria.get_tender_profile",
]

get_tender_category_targets = [
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_category",
    "openprocurement.tender.core.procedure.criteria.get_tender_category",
]

get_bid_product_targets = [
    "openprocurement.tender.core.procedure.state.bid.get_tender_product",
]


class patch_market_profile(ContextDecorator):
    def __init__(self, profile):
        self.profile = profile

    def __enter__(self):
        self.patch = patch_multiple(get_tender_profile_targets, Mock(return_value=self.profile))
        return self.patch.__enter__()

    def __exit__(self, *exc_info):
        self.patch.__exit__(*exc_info)


class patch_market_category(ContextDecorator):
    def __init__(self, category):
        self.category = category

    def __enter__(self):
        self.patch = patch_multiple(get_tender_category_targets, Mock(return_value=self.category))
        return self.patch.__enter__()

    def __exit__(self, *exc_info):
        self.patch.__exit__(*exc_info)


class patch_market_product(ContextDecorator):
    def __init__(self, product):
        self.product = product

    def __enter__(self):
        self.patch = patch_multiple(get_bid_product_targets, Mock(return_value=self.product))
        return self.patch.__enter__()

    def __exit__(self, *exc_info):
        self.patch.__exit__(*exc_info)


class patch_market(ContextDecorator):
    def __init__(self, profile, category):
        self.profile = profile
        self.category = category

    def __enter__(self):
        self.profile_patch = patch_market_profile(self.profile)
        self.category_patch = patch_market_category(self.category)
        self.profile_patch.__enter__()
        self.category_patch.__enter__()
        return self

    def __exit__(self, *exc_info):
        self.category_patch.__exit__(*exc_info)
        self.profile_patch.__exit__(*exc_info)


class MockMarketMixin:
    def setUp(self):

        # profile
        patch_obj = patch_multiple(get_tender_profile_targets, Mock(return_value=test_tender_pq_short_profile))
        patch_obj.start()
        self.addCleanup(patch_obj.stop)

        # category
        patch_obj = patch_multiple(get_tender_category_targets, Mock(return_value=test_tender_pq_category))
        patch_obj.start()
        self.addCleanup(patch_obj.stop)

        # product
        patch_obj = patch_multiple(get_bid_product_targets, Mock(return_value=test_bid_pq_product))
        patch_obj.start()
        self.addCleanup(patch_obj.stop)

        super().setUp()


class MockCriteriaIDMixin:
    def setUp(self):
        target = "openprocurement.tender.core.procedure.models.criterion.PQ_CRITERIA_ID_FROM"
        patch_obj = patch(target, get_now() + timedelta(days=1))
        patch_obj.start()
        self.addCleanup(patch_obj.stop)
        super().setUp()
