from openprocurement.api.context import get_request, get_now
from openprocurement.api.utils import raise_operation_error, error_handler
from openprocurement.planning.api.procedure.context import get_plan
from openprocurement.planning.api.procedure.models.milestone import Milestone
from openprocurement.planning.api.procedure.state.plan import PlanState


class MilestoneState(PlanState):
    def milestone_always(self, data):
        data["dateModified"] = get_now().isoformat()

    def milestone_on_post(self, data):
        self.milestone_always(data)
        self.milestone_validate_on_post(data)

    def milestone_on_patch(self, before: dict, after: dict):
        self.milestone_always(after)
        self.milestone_validate_on_patch(before, after)
        if before["status"] != after["status"]:
            self.milestone_status_up(before["status"], after["status"], after)

    def milestone_status_up(self, before, after, data):
        assert before != after, "Statuses must be different"

        # Allowed status changes: scheduled -> met/notMet
        if before == Milestone.STATUS_SCHEDULED and after in (Milestone.STATUS_MET, Milestone.STATUS_NOT_MET):
            if after == Milestone.STATUS_MET:
                data["dateMet"] = get_now().isoformat()
        else:
            raise_operation_error(self.request, "Can't update milestone status from '{}' to '{}'".format(before, after))

    def milestone_validate_on_post(self, data):
        self._validate_milestone_author(data)
        self._validate_milestone_status_scheduled(data)

    def milestone_validate_on_patch(self, before, after):
        self._milestone_validate_due_date_change(before, after)
        self._milestone_validate_description_change(before, after)

    def _validate_milestone_author(self, data):
        request = get_request()
        plan = get_plan()

        def identifier(organization):
            return (organization["identifier"]["scheme"], organization["identifier"]["id"])

        if identifier(plan["procuringEntity"]) != identifier(data["author"]):
            request.errors.add("body", "author", "Should match plan.procuringEntity")
            request.errors.status = 422
            raise error_handler(request)

        if any(
            identifier(m["author"]) == identifier(data["author"])
            for m in plan.get("milestones") or []
            if m["status"] in Milestone.ACTIVE_STATUSES
        ):
            request.errors.add("body", "author", "An active milestone already exists for this author")
            request.errors.status = 422
            raise error_handler(request)

    def _validate_milestone_status_scheduled(self, data):
        if data["status"] != Milestone.STATUS_SCHEDULED:
            request = get_request()
            request.errors.add("body", "status", "Cannot create milestone with status: {}".format(data["status"]))
            request.errors.status = 422
            raise error_handler(request)

    def _milestone_validate_due_date_change(self, before, after):
        if before["dueDate"] != after["dueDate"] and before["status"] != Milestone.STATUS_SCHEDULED:
            raise_operation_error(
                self.request, "Can't update dueDate at '{}' milestone status".format(before["status"])
            )

    def _milestone_validate_description_change(self, before, after):
        if before["description"] != after["description"] and before["status"] not in (
            Milestone.STATUS_SCHEDULED,
            Milestone.STATUS_MET,
        ):
            raise_operation_error(
                self.request, "Can't update description at '{}' milestone status".format(before["status"])
            )
