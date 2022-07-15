from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.validation import validate_lot_operation_for_stage2


@resource(
    name="{}:Lots".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender stage2 EU lots",
)
class TenderStage2EULotResource(TenderLotResource):
    @json_view(
        content_type="application/json",
        permission="create_lot",
        validators=(validate_lot_operation_for_stage2,),
    )
    def collection_post(self):
        """ Add a lot """

    @json_view(
        content_type="application/json",
        permission="edit_lot",
        validators=(validate_lot_operation_for_stage2,),
    )
    def patch(self):
        """ Update of lot """

    @json_view(
        permission="edit_lot",
        validators=(validate_lot_operation_for_stage2,),
    )
    def delete(self):
        """Lot deleting """


@resource(
    name="{}:Lots".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender stage2 UA lots",
)
class TenderStage2UALotResource(TenderLotResource):
    @json_view(
        content_type="application/json",
        permission="create_lot",
        validators=(validate_lot_operation_for_stage2,),
    )
    def collection_post(self):
        """ Add a lot """

    @json_view(
        content_type="application/json",
        permission="edit_lot",
        validators=(validate_lot_operation_for_stage2,),
    )
    def patch(self):
        """ Update of lot """

    @json_view(
        permission="edit_lot",
        validators=(validate_lot_operation_for_stage2,),
    )
    def delete(self):
        """Lot deleting """
