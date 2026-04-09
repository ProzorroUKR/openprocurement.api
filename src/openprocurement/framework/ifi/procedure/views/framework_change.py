from cornice.resource import resource

from openprocurement.framework.core.procedure.views.change import CoreChangeResource
from openprocurement.framework.ifi.constants import IFI_TYPE
from openprocurement.framework.ifi.procedure.state.change import IFIChangeState


@resource(
    name=f"{IFI_TYPE}:Framework Change",
    collection_path="/frameworks/{framework_id}/changes",
    path="/frameworks/{framework_id}/changes/{change_id}",
    frameworkType=IFI_TYPE,
    description="Framework related changes",
)
class FrameworkPeriodChangeResource(CoreChangeResource):
    state_class = IFIChangeState
