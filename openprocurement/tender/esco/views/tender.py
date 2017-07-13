# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.views.tender import TenderEUResource
from openprocurement.tender.core.utils import optendersresource


#  TODO: remove these import section after adding auction
from openprocurement.api.utils import json_view, error_handler
from openprocurement.tender.core.validation import (
    validate_tender_status_update_in_terminated_status,
    validate_tender_status_update_not_in_pre_qualificaton
)
from openprocurement.tender.openua.validation import validate_patch_tender_ua_data


#  TODO: remove this validator after adding auction
def validate_submission_method_details(request):
    submission_method_details = request.validated['data'].get("submissionMethodDetails", request.context.submissionMethodDetails)
    if submission_method_details != request.context.status and submission_method_details != 'quick(mode:no-auction)':
        request.errors.add(
                'data',
                'submissionMethodDetails',
                'Invalid field value \'{0}\'. Only \'quick(mode:no-auction)\' is allowed while auction for this type of procedure is not ready.'.
                    format(submission_method_details))
        request.errors.status = 403
        raise error_handler(request.errors)


@optendersresource(name='esco.EU:Tender',
                   path='/tenders/{tender_id}',
                   procurementMethodType='esco.EU',
                   description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderESCOEUResource(TenderEUResource):
    """ Resource handler for Tender ESCO EU """

    # TODO: remove this method after adding auction
    patch = json_view(content_type="application/json",
                      validators=(validate_patch_tender_ua_data,
                                  validate_tender_status_update_in_terminated_status,
                                  validate_tender_status_update_not_in_pre_qualificaton,
                                  validate_submission_method_details),
                      permission='edit_tender')(TenderEUResource.patch)
