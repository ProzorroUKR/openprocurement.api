from openprocurement.api.utils import json_view
from openprocurement.api.utils import (
    context_unpack,
    update_file_content_type,
)
from openprocurement.tender.core.procedure.documents import get_file, check_document, update_document_url
from openprocurement.tender.core.procedure.serializers.document import DocumentSerializer
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.models.document import Document, PostDocument, PatchDocument
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
    validate_item_owner,
    update_doc_fields_on_put_document,
    validate_upload_document,
    validate_data_model,
)
from openprocurement.tender.core.procedure.utils import (
    delete_nones,
    get_items,
    set_item,
    save_tender,
)


def resolve_document(request, item_name, container):
    match_dict = request.matchdict
    if match_dict.get("document_id"):
        document_id = match_dict["document_id"]
        documents = get_items(request, request.validated[item_name], container, document_id)
        request.validated["documents"] = documents
        request.validated["document"] = documents[-1]
    else:
        request.validated["documents"] = request.validated[item_name].get(container, tuple())


class BaseDocumentResource(TenderBaseResource):
    state_class = BaseDocumentState
    serializer_class = DocumentSerializer
    model_class = Document
    container = "documents"
    item_name = "tender"

    def set_doc_author(self, doc):   # TODO: move to state class?
        pass

    def get_modified(self):
        return True

    @json_view(permission="view_tender")
    def collection_get(self):
        collection_data = self.request.validated["documents"]
        if not self.request.params.get("all", ""):
            documents_by_id = {i["id"]: i for i in collection_data}
            collection_data = sorted(
                documents_by_id.values(),
                key=lambda i: i["dateModified"],
            )
        return {"data": [self.serializer_class(i).data for i in collection_data]}

    @json_view(
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PostDocument, allow_bulk=True),
        ),
        permission="edit_tender",
    )
    def collection_post(self):
        documents = self.request.validated["data"]
        if not isinstance(documents, list):
            documents = [documents]

        # validating and uploading magic
        for document in documents:
            check_document(self.request, document)
            document_route = self.request.matched_route.name.replace("collection_", "")
            update_document_url(self.request, document, document_route, {})

            # adding "author" field
            self.set_doc_author(document)

            # removing fields with None values
            # api doesn't save defaults and None at the moment
            delete_nones(document)

            self.state.document_on_post(document)

        # attaching documents to the bid
        item = self.request.validated[self.item_name]
        if self.container not in item:
            item[self.container] = []
        item[self.container].extend(documents)

        # saving tender
        if save_tender(self.request, modified=self.get_modified()):
            for document in documents:
                self.LOGGER.info(
                    f"Created {self.item_name} document {document['id']}",
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": f"{self.item_name}_document_create"},
                        {"document_id": document["id"]},
                    ),
                )
            self.request.response.status = 201

        if isinstance(self.request.validated["json_data"], list):  # bulk update
            return {"data": [self.serializer_class(d).data for d in documents]}
        else:
            document = documents[0]
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=document_route, document_id=document["id"], _query={}
            )
            return {"data": self.serializer_class(document).data}

    @json_view(permission="view_tender")
    def get(self):
        if self.request.params.get("download"):
            return get_file(self.request)
        document = self.request.validated["document"]
        document["previousVersions"] = [
            DocumentSerializer(i).data
            for i in self.request.validated["documents"]
            if i["url"] != document["url"]
        ]
        return {"data": self.serializer_class(document).data}

    @json_view(
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PostDocument),

            update_doc_fields_on_put_document,
            validate_upload_document,
            validate_data_model(Document),
        ),
        permission="edit_tender",
    )
    def put(self):
        document = self.request.validated["data"]

        self.state.document_on_post(document)

        item = self.request.validated[self.item_name]
        item[self.container].append(document)

        if save_tender(self.request, modified=self.get_modified()):
            self.LOGGER.info(
                f"Updated {self.item_name} document {document['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": f"{self.item_name}_document_put"}),
            )
            return {"data": self.serializer_class(document).data}

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PatchDocument, none_means_remove=True),
            validate_patch_data(Document, item_name="document"),
        ),
        permission="edit_tender",
    )
    def patch(self):
        document = self.request.validated["document"]
        updated_document = self.request.validated["data"]
        if updated_document:
            self.state.document_on_patch(document, updated_document)

            set_item(self.request.validated[self.item_name], self.container, document["id"], updated_document)

            if save_tender(self.request, modified=self.get_modified()):
                update_file_content_type(self.request)
                self.LOGGER.info(
                    f"Updated {self.item_name} document {document['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": f"{self.item_name}_document_patch"}),
                )
                return {"data": self.serializer_class(updated_document).data}
