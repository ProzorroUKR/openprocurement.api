from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.views.change import CoreChangeResource


@resource(
    name=f"{FrameworkType.DYNAMIC_PURCHASING_SYSTEM}:Framework Change",
    collection_path="/frameworks/{framework_id}/changes",
    path="/frameworks/{framework_id}/changes/{change_id}",
    frameworkType=FrameworkType.DYNAMIC_PURCHASING_SYSTEM,
    description="Framework related changes",
)
class FrameworkPeriodChangeResource(CoreChangeResource):
    pass
