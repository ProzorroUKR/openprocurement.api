from cornice.resource import resource

from openprocurement.framework.core.procedure.views.change import CoreChangeResource
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.framework.electroniccatalogue.procedure.state.change import (
    ElectronicDialogueChangeState,
)


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Framework Change",
    collection_path="/frameworks/{framework_id}/changes",
    path="/frameworks/{framework_id}/changes/{change_id}",
    frameworkType=ELECTRONIC_CATALOGUE_TYPE,
    description="Framework related changes",
)
class FrameworkPeriodChangeResource(CoreChangeResource):
    state_class = ElectronicDialogueChangeState
