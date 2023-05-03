import json

from openprocurement.api.context import get_now
import logging

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
            self.status_up(before["status"], after["status"], after)
        self.always(after)

    def always(self, data):  # post or patch
        pass

    @staticmethod
    def set_object_status(obj, status):
        if obj["status"] != status:
            obj["status"] = status
            obj["date"] = get_now().isoformat()
        else:
            logger.warning(f"Obj status already set")
