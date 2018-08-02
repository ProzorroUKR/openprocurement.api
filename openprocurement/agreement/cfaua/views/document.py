from openprocurement.api.utils import (
    json_view,
    APIResource,
    get_file
    )
from openprocurement.agreement.core.resource import (
    agreements_resource
    )


@agreements_resource(
    name='cfaua.Agreement.Document',
    collection_path='/agreements/{agreement_id}/documents',
    path='/agreements/{agreement_id}/documents/{document_id}',
    agreementType='cfaua',
    description='Agreements resource'
)
class AgreementContractsResource(APIResource):

    @json_view(permission='view_agreement')
    def collection_get(self):
        """ Agreement Documents List """
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(permission='view_agreement')
    def get(self):
        """ Agreement Document Read"""
        if self.request.params.get('download'):
            return get_file(self.request)
        document = self.request.validated['document']
        document_data = document.serialize("view")
        document_data['previousVersions'] = [
            i.serialize("view")
            for i in self.request.validated['documents']
            if i.url != document.url
        ]
        return {'data': document_data}