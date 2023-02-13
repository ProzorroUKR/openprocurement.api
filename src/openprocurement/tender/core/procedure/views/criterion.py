from logging import getLogger
from typing import Optional, List, Tuple

from pyramid.request import Request
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS

from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.core.procedure.utils import save_tender, set_item
from openprocurement.tender.core.procedure.serializers.criterion import CriterionSerializer
from openprocurement.tender.core.procedure.state.criterion import CriterionState
from openprocurement.tender.core.procedure.models.criterion import Criterion, PatchCriterion
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
)


LOGGER = getLogger(__name__)


def resolve_criterion(request: Request) -> None:
    match_dict = request.matchdict
    if match_dict.get("criterion_id"):
        criterion_id = match_dict["criterion_id"]
        criteria = get_items(request, request.validated["tender"], "criteria", criterion_id)
        request.validated["criterion"] = criteria[0]


class BaseCriterionResource(TenderBaseResource):

    def __acl__(self) -> List[Tuple[str, str, str]]:
        return [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_criterion"),
            (Allow, "g:brokers", "edit_criterion"),
            (Allow, "g:Administrator", "edit_criterion"),  # wtf ???
            (Allow, "g:admins", ALL_PERMISSIONS),    # some tests use this, idk why
        ]

    serializer_class = CriterionSerializer
    state_class = CriterionState

    def __init__(self, request: Request, context=None) -> None:
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_criterion(request)

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_input_data(Criterion, allow_bulk=True),
        ),
        permission="create_criterion",
    )
    def collection_post(self) -> Optional[dict]:

        tender = self.request.validated["tender"]
        criteria = self.request.validated["data"]
        if "criteria" not in tender:
            tender["criteria"] = []

        self.state.validate_on_post(criteria)
        tender["criteria"].extend(criteria)
        self.state.criterion_on_post(criteria)

        if save_tender(self.request):
            for criterion in criteria:
                self.LOGGER.info(
                    "Created tender criterion {}".format(criterion["id"]),
                    extra=context_unpack(
                        self.request, {"MESSAGE_ID": "tender_criterion_create"}, {"criterion_id": criterion["id"]}
                    ),
                )

            self.request.response.status = 201

            return {"data": [self.serializer_class(criterion).data for criterion in criteria]}

    @json_view(permission="view_tender")
    def collection_get(self) -> dict:
        tender = self.request.validated["tender"]
        data = tuple(self.serializer_class(criterion).data for criterion in tender.get("criteria", ""))
        return {"data": data}

    @json_view(permission="view_tender")
    def get(self) -> dict:
        data = self.serializer_class(self.request.validated["criterion"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_input_data(PatchCriterion),
                validate_patch_data_simple(Criterion, "criterion"),
        ),
        permission="edit_criterion",
    )
    def patch(self) -> Optional[dict]:
        updated_criterion = self.request.validated["data"]
        if not updated_criterion:
            return
        criterion = self.request.validated["criterion"]
        tender = self.request.validated["tender"]
        self.state.criterion_on_patch(criterion, updated_criterion)
        set_item(tender, "criteria", criterion["id"], updated_criterion)

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender criterion {}".format(criterion["id"]),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_criterion_patch"}
                ),
            )
            return {"data":  self.serializer_class(updated_criterion).data}
