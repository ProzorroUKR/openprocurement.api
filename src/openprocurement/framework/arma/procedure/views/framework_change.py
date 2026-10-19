from cornice.resource import resource

from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.arma.procedure.state.change import ARMAChangeState
from openprocurement.framework.core.procedure.views.change import CoreChangeResource


@resource(
    name=f"{ARMA_TYPE}:Framework Change",
    collection_path="/frameworks/{framework_id}/changes",
    path="/frameworks/{framework_id}/changes/{change_id}",
    frameworkType=ARMA_TYPE,
    description="Framework related changes",
)
class FrameworkPeriodChangeResource(CoreChangeResource):
    state_class = ARMAChangeState
