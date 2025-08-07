from cornice.resource import resource

from openprocurement.framework.core.procedure.views.period import (
    CorePeriodChangeResource,
)
from openprocurement.framework.dps.constants import DPS_TYPE


@resource(
    name=f"{DPS_TYPE}:Framework Period Change",
    path="/frameworks/{framework_id}/modify-period",
    frameworkType=DPS_TYPE,
    description="Framework related changes for period",
)
class FrameworkPeriodChangeResource(CorePeriodChangeResource):
    pass
