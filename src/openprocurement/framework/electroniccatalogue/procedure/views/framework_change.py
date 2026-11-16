from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.views.change import CoreChangeResource
from openprocurement.framework.electroniccatalogue.procedure.state.change import (
    ElectronicDialogueChangeState,
)


@resource(
    name=f"{FrameworkType.ELECTRONIC_CATALOGUE}:Framework Change",
    collection_path="/frameworks/{framework_id}/changes",
    path="/frameworks/{framework_id}/changes/{change_id}",
    frameworkType=FrameworkType.ELECTRONIC_CATALOGUE,
    description="Framework related changes",
)
class FrameworkPeriodChangeResource(CoreChangeResource):
    state_class = ElectronicDialogueChangeState
