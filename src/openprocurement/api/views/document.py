from openprocurement.api.views.base import BaseResource
from openprocurement.api.utils import (
    get_file,
    upload_file,
    update_file_content_type,
    context_unpack,
    upload_files,
)


class BaseDocumentResource(BaseResource):
    container = "documents"
    context_name = None

    def pre_save(self):
        pass

    def save(self, request, **kwargs):
        raise NotImplementedError

    def apply(self, request, **kwargs):
        raise NotImplementedError

    def get_doc_view_role(self, doc):
        return "view"

    def set_doc_author(self, doc):
        pass

    @property
    def context_pretty_name(self):
        if not self.context_name:
            raise NotImplementedError
        return self.context_name.replace("_", " ")

    @property
    def context_short_name(self):
        if not self.context_name:
            raise NotImplementedError
        return self.context_name.split("_")[-1]

    def collection_get(self):
        if self.request.params.get("all", ""):
            collection_data = [
                i.serialize(self.get_doc_view_role(i))
                for i in getattr(self.context, self.container)
            ]
        else:
            documents_by_id = {
                i.id: i.serialize(self.get_doc_view_role(i))
                for i in getattr(self.context, self.container)
            }
            collection_data = sorted(
                documents_by_id.values(),
                key=lambda i: i["dateModified"],
            )
        return {"data": collection_data}

    def collection_post(self):
        documents = list(upload_files(self.request, container=self.container))
        for document in documents:
            self.set_doc_author(document)
        getattr(self.context, self.container).extend(documents)

        self.pre_save()
        if self.save(self.request, validate=True):
            for document in documents:
                self.LOGGER.info(
                    "Created {} document {}".format(self.context_pretty_name, document.id),
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "{}_document_create".format(self.context_name)},
                        {"document_id": document.id},
                    ),
                )
            self.request.response.status = 201

        if "document_bulk" in self.request.validated:
            return {"data": [document.serialize("view") for document in documents]}
        else:
            document = documents[0]
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=document_route, document_id=document.id, _query={}
            )
            return {"data": document.serialize("view")}

    def get(self):
        if self.request.params.get("download"):
            return get_file(self.request)
        document = self.request.validated["document"]
        serialize_role = self.get_doc_view_role(document)
        document_data = document.serialize(serialize_role)
        document_data["previousVersions"] = [
            i.serialize(serialize_role) for i in self.request.validated["documents"] if i.url != document.url
        ]
        return {"data": document_data}

    def put(self):
        document = upload_file(self.request)
        getattr(self.request.validated[self.context_short_name], self.container).append(document)
        self.pre_save()
        if self.save(self.request):
            self.LOGGER.info(
                "Updated {} document {}".format(self.context_pretty_name, self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "{}_document_put".format(self.context_name)}),
            )
            return {"data": document.serialize("view")}

    def patch(self):
        self.pre_save()
        if self.apply(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info(
                "Updated {} document {}".format(self.context_pretty_name, self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "{}_document_patch".format(self.context_name)}),
            )
            return {"data": self.request.context.serialize("view")}
