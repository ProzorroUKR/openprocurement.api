import logging

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from openprocurement.api.context import get_request_now
from openprocurement.api.utils import raise_operation_error

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
                obj["date"] = get_request_now().isoformat()
        else:
            logger.warning("Obj status already set")


class ConfigMixin:
    default_config_schema = {}

    def get_config_schema(self, data):
        return self.default_config_schema

    def validate_config(self, data):
        config_schema = self.get_config_schema(data)
        self.validate_config_schema(data, config_schema)

    def validate_config_schema(self, data, config_schema):
        try:
            validate(data["config"], config_schema)
        except ValidationError as e:
            path = ".".join(["config"] + list(e.path))
            raise_operation_error(
                self.request,
                e.message,
                status=422,
                location="body",
                name=path,
            )
