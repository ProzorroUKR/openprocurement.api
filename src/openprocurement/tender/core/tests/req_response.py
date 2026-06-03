import unittest
from unittest.mock import patch

from schematics.exceptions import ValidationError

from openprocurement.tender.core.constants import (
    CRITERION_LOCALIZATION,
    CRITERION_TECHNICAL_FEATURES,
)
from openprocurement.tender.core.procedure.models.req_response import MatchResponseValue
from openprocurement.tender.core.procedure.validation import TYPEMAP

TENDER_CREATED_AFTER = "openprocurement.tender.core.procedure.models.req_response.tender_created_after"


class TestExtraValuesAllowed(unittest.TestCase):
    tech_criterion = {"classification": {"id": CRITERION_TECHNICAL_FEATURES}, "relatedItem": "item1"}

    def test_tech_criterion_with_linked_product(self):
        bid = {"items": [{"id": "item1", "product": "p1"}]}
        self.assertTrue(MatchResponseValue._extra_values_allowed(self.tech_criterion, bid))

    def test_localization_criterion_with_linked_product(self):
        criterion = {"classification": {"id": CRITERION_LOCALIZATION}, "relatedItem": "item1"}
        bid = {"items": [{"id": "item1", "product": "p1"}]}
        self.assertTrue(MatchResponseValue._extra_values_allowed(criterion, bid))

    def test_tech_criterion_item_without_product(self):
        bid = {"items": [{"id": "item1"}]}
        self.assertFalse(MatchResponseValue._extra_values_allowed(self.tech_criterion, bid))

    def test_tech_criterion_product_on_another_item(self):
        bid = {"items": [{"id": "item2", "product": "p1"}]}
        self.assertFalse(MatchResponseValue._extra_values_allowed(self.tech_criterion, bid))

    def test_non_tech_criterion_with_linked_product(self):
        criterion = {"classification": {"id": "CRITERION.OTHER.SOMETHING"}, "relatedItem": "item1"}
        bid = {"items": [{"id": "item1", "product": "p1"}]}
        self.assertFalse(MatchResponseValue._extra_values_allowed(criterion, bid))

    def test_tech_criterion_without_related_item(self):
        criterion = {"classification": {"id": CRITERION_TECHNICAL_FEATURES}}
        bid = {"items": [{"id": "item1", "product": "p1"}]}
        self.assertFalse(MatchResponseValue._extra_values_allowed(criterion, bid))

    def test_missing_criterion_or_parent(self):
        bid = {"items": [{"id": "item1", "product": "p1"}]}
        self.assertFalse(MatchResponseValue._extra_values_allowed(None, bid))
        self.assertFalse(MatchResponseValue._extra_values_allowed(self.tech_criterion, None))
        self.assertFalse(MatchResponseValue._extra_values_allowed(self.tech_criterion, {}))


class TestMatchExpectedValuesSubset(unittest.TestCase):
    datatype = TYPEMAP["string"]
    requirement = {"id": "r1", "expectedValues": ["A", "B"], "expectedMinItems": 1}

    def _match(self, values, allow_extra_values, requirement=None):
        with patch(TENDER_CREATED_AFTER, return_value=True):
            MatchResponseValue._match_expected_values(
                self.datatype,
                requirement or self.requirement,
                values,
                allow_extra_values=allow_extra_values,
            )

    def test_subset_enforced_when_not_allowed(self):
        with self.assertRaises(ValidationError) as ctx:
            self._match(["A", "C"], allow_extra_values=False)
        self.assertIn("One or more values are not among expected values for requirement", str(ctx.exception))

    def test_extra_value_allowed_when_allowed(self):
        self._match(["A", "C"], allow_extra_values=True)

    def test_conforming_values_pass_when_not_allowed(self):
        self._match(["A", "B"], allow_extra_values=False)

    def test_min_items_enforced_even_when_allowed(self):
        with self.assertRaises(ValidationError) as ctx:
            self._match(["C", "D"], allow_extra_values=True)
        self.assertIn("Count of matching values is less than minimum of", str(ctx.exception))

    def test_min_items_enforced_when_not_allowed(self):
        with self.assertRaises(ValidationError) as ctx:
            self._match([], allow_extra_values=False)
        self.assertIn("Count of values is less than minimum of", str(ctx.exception))

    def test_max_items_enforced_even_when_allowed(self):
        requirement = {"id": "r1", "expectedValues": ["A", "B", "C"], "expectedMinItems": 1, "expectedMaxItems": 2}
        with self.assertRaises(ValidationError) as ctx:
            self._match(["A", "B", "C"], allow_extra_values=True, requirement=requirement)
        self.assertIn("Count of values is higher than maximum of", str(ctx.exception))

    def test_max_items_enforced_when_not_allowed(self):
        requirement = {"id": "r1", "expectedValues": ["A", "B", "C"], "expectedMinItems": 1, "expectedMaxItems": 2}
        with self.assertRaises(ValidationError) as ctx:
            self._match(["A", "B", "C"], allow_extra_values=False, requirement=requirement)
        self.assertIn("Count of values is higher than maximum of", str(ctx.exception))

    def test_duplicates_dont_count_against_max(self):
        requirement = {"id": "r1", "expectedValues": ["A", "B"], "expectedMinItems": 1, "expectedMaxItems": 2}
        self._match(["A", "A", "B"], allow_extra_values=False, requirement=requirement)

    def test_extra_value_with_full_overlap_allowed(self):
        # All expected values are covered AND there's an extra one — allowed when allow_extra_values.
        requirement = {"id": "r1", "expectedValues": ["A", "B"], "expectedMinItems": 1, "expectedMaxItems": 3}
        self._match(["A", "B", "C"], allow_extra_values=True, requirement=requirement)

    def test_extra_value_with_full_overlap_rejected_when_not_allowed(self):
        requirement = {"id": "r1", "expectedValues": ["A", "B"], "expectedMinItems": 1, "expectedMaxItems": 3}
        with self.assertRaises(ValidationError) as ctx:
            self._match(["A", "B", "C"], allow_extra_values=False, requirement=requirement)
        self.assertIn("One or more values are not among expected values for requirement", str(ctx.exception))

    def test_no_expected_values_skips_subset_check(self):
        # Requirement carries no expectedValues (e.g. boolean/numeric requirement) — the subset
        # check must not fire even when allow_extra_values=False.
        requirement = {"id": "r1"}
        self._match(["X"], allow_extra_values=False, requirement=requirement)
