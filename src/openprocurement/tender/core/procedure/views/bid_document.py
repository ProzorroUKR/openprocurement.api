from openprocurement.api.utils import (
    json_view,
    context_unpack,
    update_file_content_type,
)
from openprocurement.tender.core.procedure.validation import validate_view_bid_document
from openprocurement.tender.core.procedure.documents import get_file, check_document, update_document_url
from openprocurement.tender.core.procedure.serializers.document import DocumentSerializer
from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.utils import (
    delete_nones,
    get_items,
    set_item,
    save_tender,
)


class TenderBidDocumentResource(TenderBidResource):
    serializer_class = DocumentSerializer
    model_class = Document

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            match_dict = request.matchdict
            if match_dict.get("document_id"):
                document_id = match_dict["document_id"]
                documents = get_items(request, request.validated["bid"], "documents", document_id)
                request.validated["documents"] = documents
                request.validated["document"] = documents[-1]
            else:
                request.validated["documents"] = request.validated["bid"].get("documents", tuple())

    def set_doc_author(self, doc):
        pass

    @json_view(
        validators=(
            validate_view_bid_document,
        ),
        permission="view_tender",
    )
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
        documents = self.request.validated["data"]  # list

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

        # attaching documents to the bid
        bid = self.request.validated["bid"]
        if "documents" not in bid:
            bid["documents"] = []
        bid["documents"].extend(documents)

        # saving tender
        modified = self.request.validated["tender"]["status"] != "active.tendering"
        if save_tender(self.request, modified=modified):
            for document in documents:
                self.LOGGER.info(
                    f"Created bid document {document['id']}",
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "bid_document_create"},
                        {"document_id": document["id"]},
                    ),
                )
            self.request.response.status = 201

        if isinstance(self.request.validated["json_data"], list):  # bulk update
            return {"data": documents}
        else:
            document = documents[0]
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=document_route, document_id=document["id"], _query={}
            )
            return {"data": document}

    @json_view(permission="view_tender", validators=(validate_view_bid_document,))
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

    def put(self):
        document = self.request.validated["data"]
        bid = self.request.validated["bid"]
        bid["documents"].append(document)

        modified = self.request.validated["tender"]["status"] != "active.tendering"
        if save_tender(self.request, modified=modified):
            self.LOGGER.info(
                f"Updated bid document {bid['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "bid_document_put"}),
            )
            return {"data": document}

    def patch(self):
        document = self.request.validated["document"]
        updated_document = self.request.validated["data"]
        if updated_document:
            set_item(self.request.validated["bid"], "documents", document["id"], updated_document)

            modified = self.request.validated["tender"]["status"] != "active.tendering"
            if save_tender(self.request, modified=modified):
                update_file_content_type(self.request)
                self.LOGGER.info(
                    f"Updated bid document {document['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "bid_document_patch"}),
                )
                return {"data": self.serializer_class(updated_document).data}
