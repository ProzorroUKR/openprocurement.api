# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_file,
    upload_file,
    update_file_content_type,
    json_view,
    context_unpack,
    APIResource,
    raise_operation_error,
    error_handler
)
from openprocurement.tender.core.utils import (
    save_tender, optendersresource, apply_patch,
)


class BaseDocumentResource(APIResource):
    context_name = "tender"

    @property
    def context_pretty_name(self):
        return self.context_name.replace("_", " ")

    @property
    def context_short_name(self):
        return self.context_name.split("_")[-1]

    def collection_get(self):
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    def collection_post(self):
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                'Created {} document {}'.format(self.context_pretty_name, document.id),
                extra=context_unpack(
                    self.request,
                    {'MESSAGE_ID': '{}_document_create'.format(self.context_name)},
                    {'document_id': document.id}
                ))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(
                _route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    def get(self):
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

    def put(self):
        document = upload_file(self.request)
        self.request.validated[self.context_short_name].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Updated {} document {}'.format(self.context_pretty_name, self.request.context.id),
                             extra=context_unpack(self.request,
                                                  {'MESSAGE_ID': '{}_document_put'.format(self.context_name)}))
            return {'data': document.serialize("view")}

    def patch(self):
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated {} document {}'.format(self.context_pretty_name, self.request.context.id),
                             extra=context_unpack(self.request,
                                                  {'MESSAGE_ID': '{}_document_patch'.format(self.context_name)}))
            return {'data': self.request.context.serialize("view")}
