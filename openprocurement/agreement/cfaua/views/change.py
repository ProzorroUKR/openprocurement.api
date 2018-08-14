# -*- coding: utf-8 -*-
from openprocurement.agreement.cfaua.validation import (
    validate_change_data,
    validate_agreement_change_add_not_in_allowed_agreement_status,
    validate_create_agreement_change,
    validate_patch_change_data,
    validate_agreement_change_update_not_in_allowed_change_status,
    validate_update_agreement_change_status
)
from openprocurement.agreement.core.utils import save_agreement, apply_patch
from openprocurement.agreement.cfaua.resource import agreements_resource
from openprocurement.api.utils import (
    json_view,
    APIResource,
    context_unpack,
    raise_operation_error,
    get_now
)


@agreements_resource(
    name='cfaua.Agreement_changes',
    collection_path='/agreements/{agreement_id}/changes',
    path='/agreements/{agreement_id}/changes/{change_id}',
    agreementType='cfaua',
    description='Agreements Changes'
)
class AgreementChangesResource(APIResource):
    """ Agreement changes resource """
    def __init__(self, request, context):
        super(AgreementChangesResource, self).__init__(request, context)
        self.server = request.registry.couchdb_server

    @json_view(permission='view_agreement')
    def collection_get(self):
        """ Return Agreement Changes list """
        return {'data': [i.serialize("view")
                     for i in self.request.validated['agreement'].changes]}

    @json_view(permission='view_agreement')
    def get(self):
        """ Return Agreement Change """
        return {'data': self.request.validated['change'].serialize("view")}

    @json_view(content_type="application/json", permission='edit_agreement',
               validators=(validate_change_data, validate_agreement_change_add_not_in_allowed_agreement_status,
                           validate_create_agreement_change))
    def collection_post(self):
        """ Agreement Change create """
        agreement = self.request.validated['agreement']

        change = self.request.validated['change']
        if change['dateSigned']:
            changes = agreement.get("changes", [])
            if len(changes) > 0:  # has previous changes
                last_change = agreement.changes[-1]
                last_date_signed = last_change.dateSigned
                if not last_date_signed:  # BBB old active changes
                    last_date_signed = last_change.date
                obj_str = "last active change"
            else:
                last_date_signed = agreement.dateSigned
                obj_str = "contct"

            if last_date_signed:  # BBB very old contracts
                if change['dateSigned'] < last_date_signed:
                    # Can't move validator because of code above
                    raise_operation_error(self.request,
                                          'Change dateSigned ({}) can\'t be earlier than {} dateSigned ({})'.format(
                                              change['dateSigned'].isoformat(), obj_str, last_date_signed.isoformat()))

        agreement.changes.append(change)

        if save_agreement(self.request):
            self.LOGGER.info('Created change {} of agreement {}'.format(change.id, agreement.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'agreement_change_create'},
                                                  {'change_id': change.id, 'agreement_id': agreement.id}))
            self.request.response.status = 201
            return {'data': change.serialize("view")}

    @json_view(content_type="application/json", permission='edit_agreement',
               validators=(validate_patch_change_data, validate_agreement_change_update_not_in_allowed_change_status))
    def patch(self):
        """ Agreement change edit """
        change = self.request.validated['change']
        data = self.request.validated['data']

        if 'status' in data and data['status'] != change.status:  # status change
            validate_update_agreement_change_status(self.request)
            change['date'] = get_now()

        apply_patch(self.request, save=False, src=change.serialize())

        if change['dateSigned']:
            agreement = self.request.validated['agreement']
            changes = agreement.get("changes", [])
            if len(changes) > 1:  # has previous changes
                last_change = agreement.changes[:-1][-1]
                last_date_signed = last_change.dateSigned
                if not last_date_signed:  # BBB old active changes
                    last_date_signed = last_change.date
                obj_str = "last active change"
            else:
                last_date_signed = agreement.dateSigned
                obj_str = "agreement"

            if last_date_signed:  # BBB very old agreement
                if change['dateSigned'] < last_date_signed:
                    # Can't move validator because of code above
                    raise_operation_error(self.request,
                                          'Change dateSigned ({}) can\'t be earlier than {} dateSigned ({})'.format(
                                              change['dateSigned'].isoformat(), obj_str, last_date_signed.isoformat()))

        if save_agreement(self.request):
            self.LOGGER.info('Updated agreement change {}'.format(change.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'agreement_change_patch'}))
            return {'data': change.serialize('view')}
