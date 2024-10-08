from cornice.resource import resource

from openprocurement.api.procedure.validation import validate_input_data
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.relocation.api.procedure.models.transfer import PostTransfer
from openprocurement.relocation.api.procedure.serializers.transfer import (
    TransferSerializer,
)
from openprocurement.relocation.api.procedure.utils import save_transfer, set_ownership
from openprocurement.relocation.api.procedure.views.base import TransferBaseResource


@resource(
    name="Transfers",
    path="/transfers/{transfer_id}",
    collection_path="/transfers",
    description="Transfers",
)
class TransferResource(TransferBaseResource):
    """Resource handler for Transfers"""

    serializer_class = TransferSerializer

    @json_view(permission="view_transfer")
    def get(self):
        data = self.serializer_class(self.request.validated["transfer"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        permission="create_transfer",
        validators=(validate_input_data(PostTransfer),),
    )
    def collection_post(self):
        transfer = self.request.validated["data"]
        access = set_ownership(transfer, self.request)

        self.request.validated["transfer"] = transfer
        if save_transfer(self.request, insert=True):
            self.LOGGER.info(
                "Created transfer {}".format(transfer["_id"]),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "transfer_create"},
                    {"transfer_id": transfer["_id"]},
                ),
            )
            self.request.response.status = 201

            data = self.serializer_class(self.request.validated["transfer"]).data
            return {
                "data": data,
                "access": access,
            }
