from typing import Type

from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.procedure.validation import (
    update_doc_fields_on_put_document,
    validate_data_model,
    validate_input_data,
    validate_item_owner,
    validate_patch_data,
    validate_upload_document,
)
from openprocurement.api.utils import (
    context_unpack,
    delete_nones,
    json_view,
    update_file_content_type,
)
from openprocurement.tender.core.procedure.documents import (
    check_document,
    get_file,
    update_document_url,
)
from openprocurement.tender.core.procedure.models.document import (
    Document,
    PatchDocument,
    PostDocument,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.views.base import TenderBaseResource


def resolve_document(request, item_name, container):
    match_dict = request.matchdict
    if match_dict.get("document_id"):
        document_id = match_dict["document_id"]
        documents = get_items(request, request.validated[item_name], container, document_id)
        request.validated["documents"] = documents
        request.validated["document"] = documents[-1]
    else:
        request.validated["documents"] = request.validated[item_name].get(container, tuple())


class DocumentResourceMixin:
    state_class: Type[BaseState]
    serializer_class: Type[BaseSerializer] = DocumentSerializer
    container: str = "documents"
    item_name: str

    def set_doc_author(self, doc):  # TODO: move to state class?
        pass

    def get_modified(self):
        return True

    def get_file(self):
        return get_file(self.request)

    def save(self, **kwargs):
        return save_tender(self.request, modified=self.get_modified(), **kwargs)

    def validate(self, document):
        pass

    def collection_get(self):
        collection_data = self.request.validated["documents"]
        if not self.request.params.get("all", ""):
            documents_by_id = {i["id"]: i for i in collection_data}
            collection_data = sorted(
                documents_by_id.values(),
                key=lambda i: i["dateModified"],
            )
        return {"data": [self.serializer_class(i).data for i in collection_data]}

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

            self.validate(document)
            self.state.document_on_post(document)

        # attaching documents to the bid
        item = self.request.validated[self.item_name]
        if self.container not in item:
            item[self.container] = []
        item[self.container].extend(documents)
        if "tender" in self.request.validated:
            self.state.always(self.request.validated["tender"])
        # saving item
        if self.save():
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

    def get(self):
        if self.request.params.get("download"):
            return self.get_file()
        document = self.request.validated["document"]
        document["previousVersions"] = [
            DocumentSerializer(i).data for i in self.request.validated["documents"] if i["url"] != document["url"]
        ]
        return {"data": self.serializer_class(document).data}

    def put(self):
        document = self.request.validated["data"]

        self.validate(document)
        self.state.document_on_post(document)

        item = self.request.validated[self.item_name]
        item[self.container].append(document)
        if "tender" in self.request.validated:
            self.state.always(self.request.validated["tender"])
        if self.save():
            self.LOGGER.info(
                f"Updated {self.item_name} document {document['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": f"{self.item_name}_document_put"}),
            )
            return {"data": self.serializer_class(document).data}

    def patch(self):
        document = self.request.validated["document"]
        updated_document = self.request.validated["data"]
        if updated_document:
            self.validate(document)
            self.state.document_on_patch(document, updated_document)

            set_item(self.request.validated[self.item_name], self.container, document["id"], updated_document)
            if "tender" in self.request.validated:
                self.state.always(self.request.validated["tender"])
            if self.save():
                update_file_content_type(self.request)
                self.LOGGER.info(
                    f"Updated {self.item_name} document {document['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": f"{self.item_name}_document_patch"}),
                )
                return {"data": self.serializer_class(updated_document).data}


class BaseDocumentResource(DocumentResourceMixin, TenderBaseResource):
    state_class = BaseDocumentState
    serializer_class = DocumentSerializer
    container = "documents"
    item_name = "tender"

    def save(self, **kwargs):
        return save_tender(self.request, modified=self.get_modified(), **kwargs)

    @json_view(permission="view_tender")
    def collection_get(self):
        return super().collection_get()

    @json_view(
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PostDocument, allow_bulk=True),
        ),
        permission="edit_tender",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(permission="view_tender")
    def get(self):
        return super().get()

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
        return super().put()

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
        return super().patch()
