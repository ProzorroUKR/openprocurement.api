# -*- coding: utf-8 -*-
from openprocurement.framework.core.utils import (
    save_framework,
    apply_patch,
    save_submission,
    save_qualification,
    save_agreement,
)
from openprocurement.api.views.document import BaseDocumentResource


class CoreFrameworkDocumentResource(BaseDocumentResource):
    container = "documents"
    context_name = "framework"

    def save(self, request, **kwargs):
        return save_framework(request)

    def apply(self, request, **kwargs):
        return apply_patch(request, self.context_short_name, **kwargs)


class CoreQualificationDocumentResource(BaseDocumentResource):
    container = "documents"
    context_name = "qualification"

    def save(self, request, **kwargs):
        return save_qualification(request)

    def apply(self, request, **kwargs):
        return apply_patch(request, self.context_short_name, **kwargs)


class CoreSubmissionDocumentResource(BaseDocumentResource):
    container = "documents"
    context_name = "submission"

    def save(self, request, **kwargs):
        return save_submission(request)

    def apply(self, request, **kwargs):
        return apply_patch(request, self.context_short_name, **kwargs)


class CoreAgreementDocumentResource(BaseDocumentResource):
    container = "documents"
    context_name = "agreement"

    def save(self, request, **kwargs):
        return save_agreement(request)

    def apply(self, request, **kwargs):
        return apply_patch(request, self.context_short_name, **kwargs)


class CoreMilestoneDocumentResource(BaseDocumentResource):
    container = "documents"
    context_name = "milestone"

    def save(self, request, **kwargs):
        return save_agreement(request, additional_obj_names=("milestone",))

    def apply(self, request, **kwargs):
        return apply_patch(request, "agreement", additional_obj_names=("milestone",), **kwargs)
