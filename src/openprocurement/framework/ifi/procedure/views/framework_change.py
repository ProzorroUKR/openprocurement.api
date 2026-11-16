from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.views.change import CoreChangeResource
from openprocurement.framework.ifi.procedure.state.change import IFIChangeState


@resource(
    name=f"{FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS}:Framework Change",
    collection_path="/frameworks/{framework_id}/changes",
    path="/frameworks/{framework_id}/changes/{change_id}",
    frameworkType=FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS,
    description="Framework related changes",
)
class FrameworkPeriodChangeResource(CoreChangeResource):
    state_class = IFIChangeState
