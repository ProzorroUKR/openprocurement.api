import logging

from jsonschema.exceptions import best_match
from jsonschema.validators import validator_for

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.api.procedure.validation import (
    update_doc_fields_on_put_document,
    validate_accreditation_level,
    validate_config_data,
    validate_data_documents,
    validate_data_model,
    validate_input_data,
    validate_item_owner,
    validate_patch_data,
    validate_patch_data_simple,
    validate_patch_input_data,
    validate_upload_document,
)
from openprocurement.api.utils import raise_operation_error

logger = logging.getLogger(__name__)


class BaseState:
    # request data models: the body of POST is validated against post_data_model, the body of PATCH against
    # patch_data_model and the patched object against data_model (see validate_patch_data / _simple)
    post_data_model = None
    patch_data_model = None
    data_model = None

    def __init__(self, request):
        self.request = request

    # --- request validation (access, availability of the operation, input parsing) ---
    # every view method starts with self.state.validate_<resource>_<http method>_request()
    # (validate_award_post_request, validate_document_put_request, ...); the state implements it for every method
    # of its resource, next to the <resource>_on_<http method> hooks

    def get_post_data_model(self):
        return self.post_data_model

    def get_patch_data_model(self):
        return self.patch_data_model

    def get_data_model(self):
        return self.data_model

    def is_item_owner(self, item_name, token_field_name="owner_token"):
        return is_item_owner(self.request, self.request.validated[item_name], token_field_name=token_field_name)

    def validate_item_owner(self, item_name, token_field_name="owner_token"):
        validate_item_owner(item_name, token_field_name=token_field_name)(self.request)

    def validate_any_item_owner(self, *item_names):
        """The requester must own one of the objects; the role of the first match is set"""
        for item_name in item_names:
            if self.is_item_owner(item_name):
                # complaint_owner is the documents author of both claims and complaints
                self.request.authenticated_role = "complaint_owner" if item_name == "claim" else f"{item_name}_owner"
                return
        raise_operation_error(self.request, "Forbidden", location="url", name="permission")

    def validate_accreditation_level(self, levels, item, operation, source="tender", kind_central_levels=None):
        validate_accreditation_level(
            levels=levels,
            item=item,
            operation=operation,
            source=source,
            kind_central_levels=kind_central_levels,
        )(self.request)

    def validate_input_data(self, model, allow_bulk=False, strict=True, none_means_remove=False):
        return validate_input_data(
            model,
            allow_bulk=allow_bulk,
            strict=strict,
            none_means_remove=none_means_remove,
        )(self.request)

    def validate_patch_input_data(self, model, allow_bulk=False, strict=True):
        return validate_patch_input_data(model, allow_bulk=allow_bulk, strict=strict)(self.request)

    def validate_patch_data(self, model, item_name):
        return validate_patch_data(model, item_name)(self.request)

    def validate_patch_data_simple(self, model, item_name):
        return validate_patch_data_simple(model, item_name)(self.request)

    def validate_data_model(self, model, strict=True):
        return validate_data_model(model, strict=strict)(self.request)

    def validate_config_data(self, default=None):
        return validate_config_data(default=default)(self.request)

    def validate_data_documents(self, route_key="tender_id", uid_key="_id"):
        return validate_data_documents(route_key=route_key, uid_key=uid_key)(self.request)

    def validate_upload_document(self):
        validate_upload_document(self.request)

    def update_doc_fields_on_put_document(self):
        update_doc_fields_on_put_document(self.request)

    # --- object lifecycle hooks ---

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
        # same as jsonschema.validate() without check_schema(),
        # which is the expensive part and is not needed for our static schemas
        validator = validator_for(config_schema)(config_schema)
        e = best_match(validator.iter_errors(data["config"]))
        if e is not None:
            path = ".".join(["config"] + list(e.path))
            raise_operation_error(
                self.request,
                e.message,
                status=422,
                location="body",
                name=path,
            )
