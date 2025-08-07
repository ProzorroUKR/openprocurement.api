from cornice.resource import resource

from openprocurement.framework.core.procedure.views.period import (
    CorePeriodChangeResource,
)
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Framework Period Change",
    path="/frameworks/{framework_id}/modify-period",
    frameworkType=ELECTRONIC_CATALOGUE_TYPE,
    description="Framework related changes for period",
)
class FrameworkPeriodChangeResource(CorePeriodChangeResource):
    pass
