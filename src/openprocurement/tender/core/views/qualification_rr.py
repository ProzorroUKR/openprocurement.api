# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.validation import (
    validate_requirement_response_data,
    validate_patch_requirement_response_data,
    validate_operation_qualification_requirement_response,
)
from openprocurement.tender.core.views.requirement_response import BaseRequirementResponseResource


class BaseQualificationRequirementResponseResource(BaseRequirementResponseResource):

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_qualification_requirement_response,
            validate_requirement_response_data,
        ),
        permission="edit_tender"
    )
    def collection_post(self):
        return super(BaseQualificationRequirementResponseResource, self).collection_post()

    @json_view(permission="view_tender")
    def collection_get(self):
        return super(BaseQualificationRequirementResponseResource, self).collection_get()

    @json_view(permission="view_tender")
    def get(self):
        return super(BaseQualificationRequirementResponseResource, self).get()

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_qualification_requirement_response,
            validate_patch_requirement_response_data,
        ),
        permission="edit_tender"
    )
    def patch(self):
        return super(BaseQualificationRequirementResponseResource, self).patch()

    @json_view(
        validators=(validate_operation_qualification_requirement_response,),
        permission="edit_tender",
    )
    def delete(self):
        return super(BaseQualificationRequirementResponseResource, self).delete()

