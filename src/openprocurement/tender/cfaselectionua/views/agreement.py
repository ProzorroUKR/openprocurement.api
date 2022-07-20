# -*- coding: utf-8 -*-
from openprocurement.api.utils import context_unpack, json_view, get_now, raise_operation_error
from openprocurement.tender.cfaselectionua.validation import (
    validate_patch_agreement_data,
    validate_agreement_operation_not_in_allowed_status,
)
from openprocurement.tender.cfaselectionua.utils import agreement_resource

from openprocurement.tender.core.utils import apply_patch, save_tender
from openprocurement.api.utils import json_view
from openprocurement.api.views.base import BaseResource
from openprocurement.tender.cfaselectionua.utils import check_tender_status


@agreement_resource(
    name="closeFrameworkAgreementSelectionUA:Tender Agreements",
    collection_path="/tenders/{tender_id}/agreements",
    path="/tenders/{tender_id}/agreements/{agreement_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender EU agreements",
)
class TenderAgreementResource(BaseResource):
    """ """

    @json_view(permission="view_tender")
    def collection_get(self):
        """ List contracts for award """

        return {"data": [i.serialize() for i in self.request.context.agreements]}

    @json_view(permission="view_tender")
    def get(self):
        """ Retrieving the contract for award """

        return {"data": self.request.validated["agreement"].serialize()}

    @json_view(
        content_type="application/json",
        permission="edit_agreement_selection",
        validators=(validate_patch_agreement_data, validate_agreement_operation_not_in_allowed_status),
    )
    def patch(self):
        """ Update of agreement """
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        check_tender_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender agreement {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_agreement_patch"}),
            )
            return {"data": self.request.context.serialize()}
