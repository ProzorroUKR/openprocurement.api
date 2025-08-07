from cornice.resource import resource

from openprocurement.framework.core.procedure.views.period import (
    CorePeriodChangeResource,
)
from openprocurement.framework.ifi.constants import IFI_TYPE


@resource(
    name=f"{IFI_TYPE}:Framework Period Change",
    path="/frameworks/{framework_id}/modify-period",
    frameworkType=IFI_TYPE,
    description="Framework related changes for period",
)
class FrameworkPeriodChangeResource(CorePeriodChangeResource):
    pass
