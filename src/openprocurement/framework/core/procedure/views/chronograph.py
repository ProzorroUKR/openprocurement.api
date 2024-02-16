from openprocurement.api.procedure.validation import validate_input_data
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.framework.core.procedure.models.framework import (
    FrameworkChronographData,
)
from openprocurement.framework.core.procedure.serializers.framework import (
    FrameworkSerializer,
)
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource


class FrameworkChronographResource(FrameworkBaseResource):
    serializer_class = FrameworkSerializer

    @json_view(
        permission="chronograph",
        validators=(validate_input_data(FrameworkChronographData),),
    )
    def patch(self):
        framework = self.request.validated["framework"]
        self.state.check_status(framework)
        if save_object(self.request, "framework"):
            self.LOGGER.info(
                "Updated tender by chronograph",
                extra=context_unpack(self.request, {"MESSAGE_ID": "framework_chronograph_patch"}),
            )
        return {
            "data": self.serializer_class(framework).data,
            "config": framework["config"],
        }
