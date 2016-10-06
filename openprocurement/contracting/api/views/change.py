# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    context_unpack,
    decrypt,
    encrypt,
    json_view,
    APIResource,
    get_now
)

from openprocurement.contracting.api.utils import (
    contractingresource, apply_patch, contract_serialize, set_ownership,
    save_contract)
from openprocurement.contracting.api.validation import (
    validate_change_data, validate_patch_change_data)


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
               validators=(validate_change_data,))
    def collection_post(self):
        """ Contract Change create """
        contract = self.request.validated['contract']
        if contract.status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t add contract change in current ({}) contract status'.format(contract.status))
            self.request.errors.status = 403
            return
        if contract.changes and contract.changes[-1].status == 'pending':
            self.request.errors.add('body', 'data', 'Can\'t create new contract change while any (pending) change exists')
            self.request.errors.status = 403
            return

        change = self.request.validated['change']
        contract.changes.append(change)

        if save_contract(self.request):
            self.LOGGER.info('Created change {} of contract {}'.format(change.id, contract.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_change_create'},
                                                  {'change_id': change.id, 'contract_id': contract.id}))
            self.request.response.status = 201
            return {'data': change.serialize("view")}

    @json_view(content_type="application/json", permission='edit_contract',
               validators=(validate_patch_change_data,))
    def patch(self):
        """ Contract change edit """
        change = self.request.validated['change']
        data = self.request.validated['data']

        if change.status == 'active':
            self.request.errors.add('body', 'data', 'Can\'t update contract change in current ({}) status'.format(change.status))
            self.request.errors.status = 403
            return

        if 'status' in data and data['status'] != change.status:  # status change

            if not data.get("dateSigned", ''):
                self.request.errors.add('body', 'data', 'Can\'t update contract change status. \'dateSigned\' is required.')
                self.request.errors.status = 403
                return

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
                    self.request.errors.add('body', 'data', 'Change dateSigned ({}) can\'t be earlier than {} dateSigned ({})'.format(change['dateSigned'].isoformat(), obj_str, last_date_signed.isoformat()))
                    self.request.errors.status = 403
                    return

        if save_contract(self.request):
            self.LOGGER.info('Updated contract change {}'.format(change.id),
                            extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_change_patch'}))
            return {'data': change.serialize('view')}
