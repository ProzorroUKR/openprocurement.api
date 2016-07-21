# -*- coding: utf-8 -*-
from functools import partial
from logging import getLogger
from openprocurement.api.utils import (
    context_unpack,
    decrypt,
    encrypt,
    json_view,
    APIResource
)

from openprocurement.contracting.api.utils import (
    contractingresource, apply_patch, contract_serialize, set_ownership,
    save_contract)
from openprocurement.contracting.api.validation import (
    validate_contract_data, validate_patch_contract_data)
from openprocurement.contracting.api.design import (
    FIELDS,
    contracts_by_dateModified_view,
    contracts_real_by_dateModified_view,
    contracts_test_by_dateModified_view,
    contracts_by_local_seq_view,
    contracts_real_by_local_seq_view,
    contracts_test_by_local_seq_view,
)

VIEW_MAP = {
    u'': contracts_real_by_dateModified_view,
    u'test': contracts_test_by_dateModified_view,
    u'_all_': contracts_by_dateModified_view,
}

CHANGES_VIEW_MAP = {
    u'': contracts_real_by_local_seq_view,
    u'test': contracts_test_by_local_seq_view,
    u'_all_': contracts_by_local_seq_view,
}

FEED = {
    u'dateModified': VIEW_MAP,
    u'changes': CHANGES_VIEW_MAP,
}


@contractingresource(name='Contracts',
                     path='/contracts',
                     description="Contracts")
class ContractsResource(APIResource):

    def __init__(self, request, context):
        super(ContractsResource, self).__init__(request, context)
        self.server = request.registry.couchdb_server
        self.update_after = request.registry.update_after

    @json_view(permission='view_contract')
    def get(self):
        params = {}
        pparams = {}
        fields = self.request.params.get('opt_fields', '')
        if fields:
            params['opt_fields'] = fields
            pparams['opt_fields'] = fields
            fields = fields.split(',')
            view_fields = fields + ['dateModified', 'id']
        limit = self.request.params.get('limit', '')
        if limit:
            params['limit'] = limit
            pparams['limit'] = limit
        limit = int(limit) if limit.isdigit() and (100 if fields else 1000) >= int(limit) > 0 else 100
        descending = bool(self.request.params.get('descending'))
        offset = self.request.params.get('offset', '')
        if descending:
            params['descending'] = 1
        else:
            pparams['descending'] = 1
        feed = self.request.params.get('feed', '')
        view_map = FEED.get(feed, VIEW_MAP)
        changes = view_map is CHANGES_VIEW_MAP
        if feed and feed in FEED:
            params['feed'] = feed
            pparams['feed'] = feed
        mode = self.request.params.get('mode', '')
        if mode and mode in view_map:
            params['mode'] = mode
            pparams['mode'] = mode
        view_limit = limit + 1 if offset else limit
        if changes:
            if offset:
                view_offset = decrypt(self.server.uuid, self.db.name, offset)
                if view_offset and view_offset.isdigit():
                    view_offset = int(view_offset)
                else:
                    self.request.errors.add('params', 'offset',
                                            'Offset expired/invalid')
                    self.request.errors.status = 404
                    return
            if not offset:
                view_offset = 'now' if descending else 0
        else:
            if offset:
                view_offset = offset
            else:
                view_offset = '9' if descending else ''
        list_view = view_map.get(mode, view_map[u''])
        if self.update_after:
            view = partial(list_view, self.db, limit=view_limit, startkey=view_offset, descending=descending, stale='update_after')
        else:
            view = partial(list_view, self.db, limit=view_limit, startkey=view_offset, descending=descending)
        if fields:
            if not changes and set(fields).issubset(set(FIELDS)):
                results = [
                    (dict([(i, j) for i, j in x.value.items() + [('id', x.id), ('dateModified', x.key)] if i in view_fields]), x.key)
                    for x in view()
                ]
            elif changes and set(fields).issubset(set(FIELDS)):
                results = [
                    (dict([(i, j) for i, j in x.value.items() + [('id', x.id)] if i in view_fields]), x.key)
                    for x in view()
                ]
            elif fields:
                self.LOGGER.info('Used custom fields for tenders list: {}'.format(','.join(sorted(fields))),
                            extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_list_custom'}))

                results = [
                    (contract_serialize(self.request, i[u'doc'], view_fields), i.key)
                    for i in view(include_docs=True)
                ]
        else:
            results = [
                ({'id': i.id, 'dateModified': i.value['dateModified']} if changes else {'id': i.id, 'dateModified': i.key}, i.key)
                for i in view()
            ]
        if results:
            params['offset'], pparams['offset'] = results[-1][1], results[0][1]
            if offset and view_offset == results[0][1]:
                results = results[1:]
            elif offset and view_offset != results[0][1]:
                results = results[:limit]
                params['offset'], pparams['offset'] = results[-1][1], view_offset
            results = [i[0] for i in results]
            if changes:
                params['offset'] = encrypt(self.server.uuid, self.db.name, params['offset'])
                pparams['offset'] = encrypt(self.server.uuid, self.db.name, pparams['offset'])
        else:
            params['offset'] = offset
            pparams['offset'] = offset
        data = {
            'data': results,
            'next_page': {
                "offset": params['offset'],
                "path": self.request.route_path('Contracts', _query=params),
                "uri": self.request.route_url('Contracts', _query=params)
            }
        }
        if descending or offset:
            data['prev_page'] = {
                "offset": pparams['offset'],
                "path": self.request.route_path('Contracts', _query=pparams),
                "uri": self.request.route_url('Contracts', _query=pparams)
            }
        return data

    @json_view(content_type="application/json", permission='create_contract',
               validators=(validate_contract_data,))
    def post(self):
        contract = self.request.validated['contract']

        # set_ownership(contract, self.request) TODO
        self.request.validated['contract'] = contract
        self.request.validated['contract_src'] = {}
        if save_contract(self.request):
            self.LOGGER.info('Created contract {} ({})'.format(contract.id, contract.contractID),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_create'},
                                                  {'contract_id': contract.id, 'contractID': contract.contractID or ''}))
            self.request.response.status = 201
            return {
                'data': contract.serialize("view"),
                'access': {
                    'token': contract.owner_token
                }
            }


@contractingresource(name='Contract',
                     path='/contracts/{contract_id}',
                     description="Contract")
class ContractResource(ContractsResource):

    @json_view(permission='view_contract')
    def get(self):
        return {'data': self.request.validated['contract'].serialize("view")}

    @json_view(content_type="application/json", permission='edit_contract',
               validators=(validate_patch_contract_data,))
    def patch(self):
        """Contract Edit (partial)
        """
        contract = self.request.validated['contract']
        if self.request.authenticated_role != 'Administrator' and contract.status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t update contract in current ({}) status'.format(contract.status))
            self.request.errors.status = 403
            return

        apply_patch(self.request, save=False, src=self.request.validated['contract_src'])

        if contract.status == 'terminated' and not contract.amountPaid:
            self.request.errors.add('body', 'data', 'Can\'t terminate contract while \'amountPaid\' is not set')
            self.request.errors.status = 403
            return

        if save_contract(self.request):
            self.LOGGER.info('Updated contract {}'.format(contract.id),
                            extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_patch'}))
            return {'data': contract.serialize('view')}


@contractingresource(name='Contract credentials',
                     path='/contracts/{contract_id}/credentials',
                     description="Contract credentials")
class ContractCredentialsResource(APIResource):

    def __init__(self, request, context):
        super(ContractCredentialsResource, self).__init__(request, context)
        self.server = request.registry.couchdb_server

    @json_view(permission='generate_credentials')
    def patch(self):
        contract = self.request.validated['contract']
        if contract.status != "active":
            self.request.errors.add('body', 'data', 'Can\'t generate credentials in current ({}) contract status'.format(contract.status))
            self.request.errors.status = 403
            return

        set_ownership(contract, self.request)
        if save_contract(self.request):
            self.LOGGER.info('Generate Contract credentials {}'.format(contract.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_patch'}))
            return {
                'data': contract.serialize("view"),
                'access': {
                    'token': contract.owner_token
                }
            }
