import logging

from openprocurement.api.context import get_now

logger = logging.getLogger(__name__)


class BaseState:
    def __init__(self, request):
        self.request = request

    def status_up(self, before, after, data):
        assert before != after, "Statuses must be different"

    def on_post(self, data):
        self.always(data)

    def on_patch(self, before, after):
        # if status has changed, we should take additional actions according to procedure
        if "status" in after and before.get("status") != after["status"]:
            self.status_up(before.get("status"), after["status"], after)
        self.always(after)

    def always(self, data):  # post or patch
        pass

    @staticmethod
    def set_object_status(obj, status, update_date=True):
        if obj.get("status") != status:
            obj["status"] = status
            if update_date:
                obj["date"] = get_now().isoformat()
        else:
            logger.warning("Obj status already set")
