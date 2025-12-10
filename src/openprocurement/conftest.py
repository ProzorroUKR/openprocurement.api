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
