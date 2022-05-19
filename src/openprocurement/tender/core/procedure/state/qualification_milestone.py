from openprocurement.tender.core.procedure.state.base import BaseState
from openprocurement.tender.core.procedure.models.qualification_milestone import QualificationMilestoneCodes
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.utils import raise_operation_error
from logging import getLogger


LOGGER = getLogger(__name__)


class QualificationMilestoneState(BaseState):

    def validate_post(self, context_name, parent, *_):
        parent_status = parent.get("status")
        if parent_status != "pending":
            raise_operation_error(
                get_request(),
                f"Not allowed in current '{parent_status}' {context_name} status"
            )

        if any(m.get("code") == QualificationMilestoneCodes.CODE_24_HOURS.value
               for m in parent.get("milestones", "")):
            raise_operation_error(
                get_request(),
                [{"milestones": ["There can be only one '24h' milestone"]}],
                status=422,
                name=f"{context_name}s"
            )
