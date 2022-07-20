# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    raise_operation_error,
)
from openprocurement.api.views.base import BaseResource
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

AGREEMENT_DEPENDENT_FIELDS = ("qualificationPeriod", "procuringEntity")


@frameworksresource(
    name="electronicCatalogue:Frameworks",
    path="/frameworks/{framework_id}",
    frameworkType="electronicCatalogue",
    description="See https://standard.open-contracting.org/latest/en/guidance/map/related_processes/",
)
class FrameworkResource(BaseResource):
    @json_view(permission="view_framework")
    def get(self):
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

            if (
                    any([f in self.request.validated["json_data"] for f in AGREEMENT_DEPENDENT_FIELDS])
                    and framework.agreementID
                    and self.request.validated["agreement_src"]["status"] == "active"
            ):
                self.update_agreement()

        self.LOGGER.info("Updated framework {}".format(framework.id),
                         extra=context_unpack(self.request, {"MESSAGE_ID": "framework_patch"}))
        # TODO: Change to chronograph_view for chronograph
        return {"data": framework.serialize(framework.status)}

    def update_agreement(self):
        framework = self.request.validated["framework"]

        updated_agreement_data = {
            "period": {
                "startDate": self.request.validated["agreement_src"]["period"]["startDate"],
                "endDate": framework.qualificationPeriod.endDate.isoformat()
            },
            "procuringEntity": framework.procuringEntity
        }
        apply_patch(
            self.request, src=self.request.validated["agreement_src"], data=updated_agreement_data, obj_name="agreement"
        )
        self.LOGGER.info("Updated agreement {}".format(self.request.validated["agreement_src"]["id"]),
                         extra=context_unpack(self.request, {"MESSAGE_ID": "framework_patch"}))
