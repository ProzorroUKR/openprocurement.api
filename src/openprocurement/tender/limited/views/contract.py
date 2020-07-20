# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, context_unpack, get_now, raise_operation_error
from openprocurement.tender.core.utils import apply_patch, save_tender, optendersresource
from openprocurement.tender.core.validation import (
    validate_contract_data,
    validate_patch_contract_data,
    validate_update_contract_value,
    validate_update_contract_value_with_award,
    validate_update_contract_value_amount,
    validate_update_contract_value_net_required,
)
from openprocurement.tender.belowthreshold.views.contract import (
    TenderAwardContractResource as BaseTenderAwardContractResource,
)
from openprocurement.tender.limited.validation import (
    validate_contract_update_in_cancelled,
    validate_contract_operation_not_in_active,
    validate_contract_items_count_modification,
    validate_contract_with_cancellations_and_contract_signing,
)


def check_tender_status(request):
    tender = request.validated["tender"]
    if tender.contracts and tender.contracts[-1].status == "active":
        tender.status = "complete"


def check_tender_negotiation_status(request):
    tender = request.validated["tender"]
    now = get_now()
    if tender.lots:
        for lot in tender.lots:
            if lot.status != "active":
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            if not lot_awards:
                continue
            last_award = lot_awards[-1]
            pending_awards_complaints = any(
                [i.status in ["claim", "answered", "pending"] for a in lot_awards for i in a.complaints]
            )
            stand_still_end = max([
                a.complaintPeriod.endDate
                if a.complaintPeriod and a.complaintPeriod.endDate else now
                for a in lot_awards
            ])
            if pending_awards_complaints or not stand_still_end <= now:
                continue
            elif last_award.status == "unsuccessful":
                lot.status = "unsuccessful"
                continue
            elif last_award.status == "active" and any(
                [i.status == "active" and i.awardID == last_award.id for i in tender.contracts]
            ):
                lot.status = "complete"
        statuses = set([lot.status for lot in tender.lots])
        if statuses == set(["cancelled"]):
            tender.status = "cancelled"
        elif not statuses.difference(set(["unsuccessful", "cancelled"])):
            tender.status = "unsuccessful"
        elif not statuses.difference(set(["complete", "unsuccessful", "cancelled"])):
            tender.status = "complete"
    else:
        if tender.contracts and tender.contracts[-1].status == "active":
            tender.status = "complete"


@optendersresource(
    name="reporting:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType="reporting",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class TenderAwardContractResource(BaseTenderAwardContractResource):
    @json_view(
        content_type="application/json",
        permission="create_contract",
        validators=(validate_contract_data, validate_contract_operation_not_in_active),
    )
    def collection_post(self):
        """Post a contract for award
        """
        tender = self.request.validated["tender"]
        contract = self.request.validated["contract"]
        tender.contracts.append(contract)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender contract {}".format(contract.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_contract_create"}, {"contract_id": contract.id}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Contracts".format(tender.procurementMethodType),
                tender_id=tender.id,
                contract_id=contract["id"],
            )
            return {"data": contract.serialize()}

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_patch_contract_data,
            validate_contract_operation_not_in_active,
            validate_contract_update_in_cancelled,
            validate_update_contract_value,
            validate_update_contract_value_net_required,
            validate_update_contract_value_with_award,
            validate_update_contract_value_amount,
            validate_contract_items_count_modification,
        ),
    )
    def patch(self):
        """Update of contract
        """
        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        self.request.context.date = get_now()
        if (
            contract_status != self.request.context.status
            and contract_status != "pending"
            and self.request.context.status != "active"
        ):
            raise_operation_error(self.request, "Can't update contract status")

        if self.request.context.status == "active" and not self.request.context.dateSigned:
            self.request.context.dateSigned = get_now()
        check_tender_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender contract {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_contract_patch"}),
            )
            return {"data": self.request.context.serialize()}


@optendersresource(
    name="negotiation:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType="negotiation",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class TenderNegotiationAwardContractResource(TenderAwardContractResource):
    """ Tender Negotiation Award Contract Resource """

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_patch_contract_data,
            validate_contract_operation_not_in_active,
            validate_contract_update_in_cancelled,
            validate_contract_with_cancellations_and_contract_signing,
            validate_update_contract_value,
            validate_update_contract_value_net_required,
            validate_update_contract_value_with_award,
            validate_update_contract_value_amount,
            validate_contract_items_count_modification,
        ),
    )
    def patch(self):
        """Update of contract
        """
        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        self.request.context.date = get_now()
        if (
            contract_status != self.request.context.status
            and contract_status != "pending"
            and self.request.context.status != "active"
        ):
            raise_operation_error(self.request, "Can't update contract status")

        if self.request.context.status == "active" and not self.request.context.dateSigned:
            self.request.context.dateSigned = get_now()
        check_tender_negotiation_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender contract {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_contract_patch"}),
            )
            return {"data": self.request.context.serialize()}


@optendersresource(
    name="negotiation.quick:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType="negotiation.quick",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class TenderNegotiationQuickAwardContractResource(TenderNegotiationAwardContractResource):
    """ Tender Negotiation Quick Award Contract Resource """
