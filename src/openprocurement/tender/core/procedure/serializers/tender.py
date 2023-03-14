from openprocurement.tender.core.procedure.serializers.base import BaseUIDSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.bid import BidSerializer
from openprocurement.tender.core.procedure.serializers.cancellation import CancellationSerializer
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer
from openprocurement.tender.core.procedure.serializers.award import AwardSerializer
from openprocurement.tender.core.procedure.serializers.lot import LotSerializer
from openprocurement.tender.core.procedure.models.tender import Guarantee
from openprocurement.api.models import Value

from schematics.types.compound import ModelType
from schematics.types.serializable import serializable


class TenderBaseSerializer(BaseUIDSerializer):
    base_private_fields = {
        "dialogue_token",
        "transfer_token",
        "_rev",
        "doc_type",
        "rev",
        "owner_token",
        "revisions",
        "numberOfBids",
        "public_modified",
        "is_public",
        "is_test",
        "config",
    }
    serializers = {
        "bids": ListSerializer(BidSerializer),
        "cancellations": ListSerializer(CancellationSerializer),
        "complaints": ListSerializer(ComplaintSerializer),
        "awards": ListSerializer(AwardSerializer),
        "lots": ListSerializer(LotSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)

        self.private_fields = set(self.base_private_fields)

        if data.get("status") in ("draft", "active.enquiries", "active.tendering", "active.auction"):
            self.private_fields.add("bids")

        # @serializable(serialized_name="value", type=ModelType(Value))
        # def tender_value(self):
        #     if self.lots:
        #         value = Value(
        #             dict(
        #                 amount=sum([i.value.amount for i in self.lots]),
        #                 currency=self.value.currency,
        #                 valueAddedTaxIncluded=self.value.valueAddedTaxIncluded,
        #             )
        #         )
        #         return value
        #     return self.value
        #
        # @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
        # def tender_guarantee(self):
        #     if self.lots:
        #         lots_amount = [i.guarantee.amount for i in self.lots if i.guarantee]
        #         if not lots_amount:
        #             return self.guarantee
        #         guarantee = {"amount": sum(lots_amount)}
        #         lots_currency = [i.guarantee.currency for i in self.lots if i.guarantee]
        #         guarantee["currency"] = lots_currency[0] if lots_currency else None
        #         if self.guarantee:
        #             guarantee["currency"] = self.guarantee.currency
        #         return Guarantee(guarantee)
        #     else:
        #         return self.guarantee
        #
        # @serializable(serialized_name="minimalStep", type=ModelType(Value))
        # def tender_minimalStep(self):
        #     return (
        #         Value(
        #             dict(
        #                 amount=min([i.minimalStep.amount for i in self.lots]),
        #                 currency=self.minimalStep.currency,
        #                 valueAddedTaxIncluded=self.minimalStep.valueAddedTaxIncluded,
        #             )
        #         )
        #         if self.lots
        #         else self.minimalStep
        #     )

