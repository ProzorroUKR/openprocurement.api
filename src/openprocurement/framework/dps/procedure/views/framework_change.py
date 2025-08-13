from cornice.resource import resource

from openprocurement.framework.core.procedure.views.change import CoreChangeResource
from openprocurement.framework.dps.constants import DPS_TYPE


@resource(
    name=f"{DPS_TYPE}:Framework Change",
    collection_path="/frameworks/{framework_id}/changes",
    path="/frameworks/{framework_id}/changes/{change_id}",
    frameworkType=DPS_TYPE,
    description="Framework related changes",
)
class FrameworkPeriodChangeResource(CoreChangeResource):
    pass
