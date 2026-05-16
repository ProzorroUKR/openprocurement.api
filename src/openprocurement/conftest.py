from datetime import timedelta

import pytest

from openprocurement.api.utils import get_now
from openprocurement.framework.core.procedure.state import framework
from openprocurement.tender.core.procedure.state import tender


@pytest.fixture(autouse=True)
def patch_tender_procurement_entity_kind_validation_from_constant(monkeypatch):
    """
    Function patches constants:
    - openprocurement.tender.core.procedure.state.tender.PROCUREMENT_ENTITY_KIND_VALIDATION_FROM constant
    - openprocurement.framework.core.procedure.state.framework.PROCUREMENT_ENTITY_KIND_VALIDATION_FROM constant
    in order to disable validation function
    """
    monkeypatch.setattr(framework, "PROCUREMENT_ENTITY_KIND_VALIDATION_FROM", get_now() + timedelta(days=1))
    monkeypatch.setattr(tender, "PROCUREMENT_ENTITY_KIND_VALIDATION_FROM", get_now() + timedelta(days=1))


@pytest.fixture(autouse=True)
def disable_feed_watermark(monkeypatch):
    """
    Disable the feed watermark delay for tests.
    Without this, freshly created documents are filtered out of the forward feed
    (public_modified < NOW - FEED_WATERMARK_SECONDS), causing feed listing tests to fail.

    When FEED_WATERMARK_SECONDS=0, the $expr filter is skipped entirely in list()
    (not just made a no-op), so this fixture is safe even for MongoDB versions
    that don't support $$NOW in find/$expr.
    """
    import openprocurement.api.database as db_module

    monkeypatch.setattr(db_module, "FEED_WATERMARK_SECONDS", 0)
