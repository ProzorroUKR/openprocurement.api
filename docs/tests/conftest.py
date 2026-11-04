from datetime import timedelta

import pytest
from dateutil.parser import parse

from openprocurement.framework.core.procedure.state import framework
from openprocurement.tender.core.procedure.state import tender, tender_details
from tests.base.constants import MOCK_DATETIME

# -------------------------------------------------
# ATTENTION! ACHTUNG!
# Avoid patching constants for docs tests globally.
# It's important to keep it as clean as possible.
# So docs show real latest API functionality.
# -------------------------------------------------


@pytest.fixture(autouse=True)
def patch_tender_procurement_entity_kind_validation_from_constant(monkeypatch):
    monkeypatch.setattr(
        framework, "PROCUREMENT_ENTITY_KIND_VALIDATION_FROM", parse(MOCK_DATETIME) + timedelta(days=365)
    )
    monkeypatch.setattr(tender, "PROCUREMENT_ENTITY_KIND_VALIDATION_FROM", parse(MOCK_DATETIME) + timedelta(days=365))


@pytest.fixture(autouse=True)
def patch_law_4888_procurement_method_types_constants(monkeypatch):
    monkeypatch.setattr(tender_details, "LAW_4888_PROCUREMENT_METHOD_TYPES_ENABLED", [])
    monkeypatch.setattr(tender_details, "LAW_4888_PROCUREMENT_METHOD_TYPES_DISABLED", [])


@pytest.fixture(autouse=True)
def disable_feed_watermark(monkeypatch):
    """
    Disable the feed watermark delay for tests.
    Without this, freshly created documents are filtered out of the forward feed
    (public_modified < NOW - FEED_WATERMARK_SECONDS), causing feed listing tests to fail.
    """
    import openprocurement.api.database as db_module

    monkeypatch.setattr(db_module, "FEED_WATERMARK_SECONDS", 0)
