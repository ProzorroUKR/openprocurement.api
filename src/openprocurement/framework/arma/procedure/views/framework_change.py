from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.framework.arma.procedure.state.change import ARMAChangeState
from openprocurement.framework.core.procedure.views.change import CoreChangeResource


@resource(
    name=f"{FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY}:Framework Change",
    collection_path="/frameworks/{framework_id}/changes",
    path="/frameworks/{framework_id}/changes/{change_id}",
    frameworkType=FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY,
    description="Framework related changes",
)
class FrameworkPeriodChangeResource(CoreChangeResource):
    state_class = ARMAChangeState
