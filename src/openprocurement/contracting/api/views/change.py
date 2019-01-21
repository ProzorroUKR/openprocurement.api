# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    context_unpack,
    decrypt,
    encrypt,
    json_view,
    APIResource,
    get_now,
    raise_operation_error
)

from openprocurement.contracting.api.utils import (
    contractingresource, apply_patch, contract_serialize, set_ownership,
    save_contract)
from openprocurement.contracting.api.validation import (
    validate_change_data,
    validate_patch_change_data,
    validate_create_contract_change,
    validate_update_contract_change_status,
    validate_contract_change_add_not_in_allowed_contract_status,
    validate_contract_change_update_not_in_allowed_change_status
)


@contractingresource(name='Contract changes',
                     collection_path='/contracts/{contract_id}/changes',
                     path='/contracts/{contract_id}/changes/{change_id}',
                     description="Contracts Changes")
class ContractsChangesResource(APIResource):
    """ Contract changes resource """

    def __init__(self, request, context):
        super(ContractsChangesResource, self).__init__(request, context)
        self.server = request.registry.couchdb_server

    @json_view(permission='view_contract')
    def collection_get(self):
        """ Return Contract Changes list """
        return {'data': [i.serialize("view")
                         for i in self.request.validated['contract'].changes]}

    @json_view(permission='view_contract')
    def get(self):
        """ Return Contract Change """
        return {'data': self.request.validated['change'].serialize("view")}

    @json_view(content_type="application/json", permission='edit_contract',
               validators=(validate_change_data, validate_contract_change_add_not_in_allowed_contract_status, validate_create_contract_change))
    def collection_post(self):
        """ Contract Change create """
        contract = self.request.validated['contract']

        change = self.request.validated['change']
        if change['dateSigned']:
            changes = contract.get("changes", [])
            if len(changes) > 0:  # has previous changes
                last_change = contract.changes[-1]
                last_date_signed = last_change.dateSigned
                if not last_date_signed:  # BBB old active changes
                    last_date_signed = last_change.date
                obj_str = "last active change"
            else:
                last_date_signed = contract.dateSigned
                obj_str = "contract"

            if last_date_signed:  # BBB very old contracts
                if change['dateSigned'] < last_date_signed:
                    # Can't move validator because of code above
                    raise_operation_error(self.request,  'Change dateSigned ({}) can\'t be earlier than {} dateSigned ({})'.format(change['dateSigned'].isoformat(), obj_str, last_date_signed.isoformat()))

        contract.changes.append(change)

        if save_contract(self.request):
            self.LOGGER.info('Created change {} of contract {}'.format(change.id, contract.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_change_create'},
                                                  {'change_id': change.id, 'contract_id': contract.id}))
            self.request.response.status = 201
            return {'data': change.serialize("view")}

    @json_view(content_type="application/json", permission='edit_contract',
               validators=(validate_patch_change_data, validate_contract_change_update_not_in_allowed_change_status))
    def patch(self):
        """ Contract change edit """
        change = self.request.validated['change']
        data = self.request.validated['data']

        if 'status' in data and data['status'] != change.status:  # status change
            validate_update_contract_change_status(self.request)
            change['date'] = get_now()

        apply_patch(self.request, save=False, src=change.serialize())

        if change['dateSigned']:
            contract = self.request.validated['contract']
            changes = contract.get("changes", [])
            if len(changes) > 1:  # has previous changes
                last_change = contract.changes[:-1][-1]
                last_date_signed = last_change.dateSigned
                if not last_date_signed:  # BBB old active changes
                    last_date_signed = last_change.date
                obj_str = "last active change"
            else:
                last_date_signed = contract.dateSigned
                obj_str = "contract"

            if last_date_signed:  # BBB very old contracts
                if change['dateSigned'] < last_date_signed:
                    # Can't move validator because of code above
                    raise_operation_error(self.request,  'Change dateSigned ({}) can\'t be earlier than {} dateSigned ({})'.format(change['dateSigned'].isoformat(), obj_str, last_date_signed.isoformat()))

        if save_contract(self.request):
            self.LOGGER.info('Updated contract change {}'.format(change.id),
                            extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_change_patch'}))
            return {'data': change.serialize('view')}
