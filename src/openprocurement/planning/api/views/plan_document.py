# -*- coding: utf-8 -*-
from openprocurement.planning.api.utils import save_plan, opresource, apply_patch, APIResource
from openprocurement.api.utils import get_file, update_file_content_type, upload_file, context_unpack, json_view
from openprocurement.planning.api.validation import validate_plan_not_terminated
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data


@opresource(
    name="Plan Documents",
    collection_path="/plans/{plan_id}/documents",
    path="/plans/{plan_id}/documents/{document_id}",
    description="Plan related binary files (PDFs, etc.)",
)
class PlansDocumentResource(APIResource):
    @json_view(permission="view_plan")
    def collection_get(self):
        """Plan Documents List"""
        if self.request.params.get("all", ""):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(
                dict([(i.id, i.serialize("view")) for i in self.context.documents]).values(),
                key=lambda i: i["dateModified"],
            )
        return {"data": collection_data}

    @json_view(permission="upload_plan_documents", validators=(validate_file_upload, validate_plan_not_terminated))
    def collection_post(self):
        """Plan Document Upload"""
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_plan(self.request):
            self._post_document_log(document)
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=document_route, document_id=document.id, _query={}
            )
            return {"data": document.serialize("view")}

    @json_view(permission="view_plan")
    def get(self):
        """Plan Document Read"""
        if self.request.params.get("download"):
            return get_file(self.request)
        document = self.request.validated["document"]
        document_data = document.serialize("view")
        document_data["previousVersions"] = [
            i.serialize("view") for i in self.request.validated["documents"] if i.url != document.url
        ]
        return {"data": document_data}

    @json_view(permission="upload_plan_documents", validators=(validate_file_update, validate_plan_not_terminated))
    def put(self):
        """Plan Document Update"""
        document = upload_file(self.request)
        self.request.context.__parent__.documents.append(document)
        if save_plan(self.request):
            self._put_document_log()
            return {"data": document.serialize("view")}

    @json_view(
        content_type="application/json",
        permission="upload_plan_documents",
        validators=(validate_patch_document_data, validate_plan_not_terminated),
    )
    def patch(self):
        """Plan Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self._patch_document_log()
            return {"data": self.request.context.serialize("view")}

    def _post_document_log(self, document):
        self.LOGGER.info(
            "Created plan document {}".format(document.id),
            extra=context_unpack(
                self.request, {"MESSAGE_ID": "plan_document_create"}, {"document_id": document.id}
            ),
        )

    def _put_document_log(self):
        self.LOGGER.info(
            "Updated plan document {}".format(self.request.context.id),
            extra=context_unpack(self.request, {"MESSAGE_ID": "plan_document_put"}),
        )

    def _patch_document_log(self):
        self.LOGGER.info(
            "Updated plan document {}".format(self.request.context.id),
            extra=context_unpack(self.request, {"MESSAGE_ID": "plan_document_patch"}),
        )
