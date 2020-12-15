from openprocurement.api.utils import (
    APIResource,
    json_view,
    context_unpack,
    raise_operation_error,
)
from openprocurement.framework.core.utils import (
    frameworksresource,
    apply_patch,
    save_framework,
)
from openprocurement.framework.core.validation import validate_patch_framework_data
from openprocurement.framework.electroniccatalogue.utils import calculate_framework_periods, check_status
from openprocurement.framework.electroniccatalogue.validation import (
    validate_ec_framework_patch_status,
    validate_qualification_period_duration
)


@frameworksresource(
    name="electronicCatalogue:Framework",
    path="/frameworks/{framework_id}",
    frameworkType="electronicCatalogue",
    description="",  # TODO: add description
)
class FrameworkResource(APIResource):
    @json_view(permission="view_framework")
    def get(self):
        """"""  # TODO: Add doc
        if self.request.authenticated_role == "chronograph":
            framework_data = self.context.serialize("chronograph_view")
        else:
            framework_data = self.context.serialize(self.context.status)
        return {"data": framework_data}

    @json_view(
        content_type="application/json",
        validators=(
                validate_patch_framework_data,
                validate_ec_framework_patch_status,
        ),
        permission="edit_framework",
    )
    def patch(self):
        """"""  # TODO: Add doc
        framework = self.context
        if self.request.authenticated_role == "chronograph":
            check_status(self.request)
            save_framework(self.request)
        else:
            if self.request.validated["data"].get("status") not in ("draft", "active"):
                raise_operation_error(
                    self.request, "Can't switch to {} status".format(self.request.validated["data"].get("status"))
                )
            if self.request.validated["data"].get("status") == "active":
                model = self.request.context._fields["qualificationPeriod"]
                calculate_framework_periods(self.request, model)
                validate_qualification_period_duration(self.request, model)

            apply_patch(self.request, src=self.request.validated["framework_src"], obj_name="framework")
        self.LOGGER.info("Updated framework {}".format(framework.id),
                         extra=context_unpack(self.request, {"MESSAGE_ID": "framework_patch"}))
        # TODO: Change to chronograph_view for chronograph
        return {"data": framework.serialize(framework.status)}
