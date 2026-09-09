from cornice.service import get_services

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.tender.core.procedure.registry import (
    PROCEDURE_MODELS,
    ProcedureModels,
    get_procedure_models,
)


class RegistryCoverageTest(BaseWebTest):
    def test_registry_covers_all_registered_procedures(self):
        """every procurementMethodType served by tender views has an entry in the registry"""
        served = {
            s.procurementMethodType
            for s in get_services()
            if getattr(s, "procurementMethodType", None) and s.path.startswith("/tenders")
        }
        self.assertTrue(served, "no tender services found")
        self.assertFalse(served - set(PROCEDURE_MODELS), served - set(PROCEDURE_MODELS))


def test_registry_models_are_core_models():
    for pmt, models in PROCEDURE_MODELS.items():
        assert isinstance(models, ProcedureModels)
        for field in ProcedureModels.__dataclass_fields__:
            model = getattr(models, field)
            if model is not None:
                assert issubclass(model, Model), (pmt, field)
                # generic models live in core, procedure-specific ones in the procedure package
                assert (
                    model.__module__.startswith("openprocurement.tender.") and ".procedure.models." in model.__module__
                ), (
                    pmt,
                    field,
                )
        assert models.tender is not None and models.tender_post is not None and models.tender_patch is not None


def test_get_procedure_models_unknown():
    try:
        get_procedure_models("unknown")
    except KeyError as e:
        assert "unknown" in str(e)
    else:
        raise AssertionError("KeyError expected")
