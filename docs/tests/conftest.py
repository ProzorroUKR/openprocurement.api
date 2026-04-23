from datetime import timedelta

import pytest
from dateutil.parser import parse

from openprocurement.framework.core.procedure.state import framework
from openprocurement.tender.core.procedure.state import tender
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
