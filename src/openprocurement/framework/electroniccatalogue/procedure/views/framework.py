# -*- coding: utf-8 -*-
from cornice.resource import resource

from openprocurement.api.auth import ACCR_1, ACCR_3, ACCR_5
from openprocurement.api.procedure.validation import (
    validate_accreditation_level,
    validate_config_data,
    validate_data_documents,
    validate_input_data,
    validate_input_data_from_resolved_model,
    validate_item_owner,
    validate_patch_data,
)
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.models.framework import FrameworkConfig
from openprocurement.framework.core.procedure.validation import (
    unless_administrator_or_chronograph,
)
from openprocurement.framework.core.procedure.views.framework import FrameworksResource
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.framework.electroniccatalogue.procedure.models.framework import (
    Framework,
    PostFramework,
)
from openprocurement.framework.electroniccatalogue.procedure.state.framework import (
    ElectronicDialogueFrameworkState,
)


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Frameworks",
    collection_path="/frameworks",
    path="/frameworks/{framework_id}",
    description=f"{ELECTRONIC_CATALOGUE_TYPE} frameworks",
    frameworkType=ELECTRONIC_CATALOGUE_TYPE,
    accept="application/json",
)
class ElectronicCatalogueFrameworkResource(FrameworksResource):
    state_class = ElectronicDialogueFrameworkState

    @json_view(
        content_type="application/json",
        permission="create_framework",
        validators=(
            validate_input_data(PostFramework),
            validate_config_data(FrameworkConfig),
            validate_accreditation_level(
                levels=(ACCR_1, ACCR_3, ACCR_5),
                kind_central_levels=(ACCR_5,),
                item="framework",
                operation="creation",
                source="data",
            ),
            validate_data_documents(route_key="framework_id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            unless_administrator_or_chronograph(validate_item_owner("framework")),
            validate_input_data_from_resolved_model(),
            validate_patch_data(Framework, item_name="framework"),
        ),
        permission="edit_framework",
    )
    def patch(self):
        return super().patch()
