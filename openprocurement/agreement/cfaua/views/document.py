from openprocurement.api.utils import (
    json_view,
    APIResource,
    get_file,
    upload_file,
    update_file_content_type
    )
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data
    )
from openprocurement.agreement.core.resource\
    import agreements_resource
from openprocurement.agreement.core.utils\
    import context_unpack, save_agreement, apply_patch
from openprocurement.agreement.cfaua.validation\
    import validate_document_operation_on_agreement_status


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


    @json_view(
        permission='upload_agreement_documents',
        validators=(
            validate_file_upload,
            validate_document_operation_on_agreement_status
        )
    )
    def collection_post(self):
        """ Agreement Document Upload"""
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_agreement(self.request):
            self.LOGGER.info(
                'Created agreement document {}'.format(document.id),
                extra=context_unpack(
                    self.request,
                    {'MESSAGE_ID': 'agreement_document_create'},
                    {'document_id': document.id}
                )
            )
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(
                _route_name=document_route, document_id=document.id, _query={}
            )
            return {'data': document.serialize("view")}

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

    @json_view(
        permission='upload_agreement_documents',
        validators=(
            validate_file_update,
            validate_document_operation_on_agreement_status
        )
    )
    def put(self):
        """ Agreement Document Update"""
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_agreement(self.request):
            self.LOGGER.info(
                'Updated agreement document {}'.format(self.request.context.id),
                extra=context_unpack(
                    self.request,
                    {'MESSAGE_ID': 'agreement_document_put'}
                )
            )
            return {'data': document.serialize("view")}

    @json_view(
        content_type="application/json",
        permission='upload_agreement_documents',
        validators=(
            validate_patch_document_data,
            validate_document_operation_on_agreement_status
        )
    )
    def patch(self):
        """ Agreement Document Update """
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info(
                'Updated agreement document {}'.format(self.request.context.id),
                extra=context_unpack(
                    self.request,
                    {'MESSAGE_ID': 'agreement_document_patch'}
                )
            )
            return {'data': self.request.context.serialize("view")}