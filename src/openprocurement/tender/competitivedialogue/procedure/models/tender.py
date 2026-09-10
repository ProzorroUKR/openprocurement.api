from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.types import ListType
from openprocurement.api.validation import validate_uniq_id
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE,
    CD_UA_TYPE,
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.models.item import CDItem
from openprocurement.tender.core.procedure.models.criterion import Criterion, validate_criteria_requirement_uniq
from openprocurement.tender.core.procedure.models.tender import (
    PatchTender,
    PostTender,
    Tender,
    validate_cd_shortlisted_firm_ids,
)
from openprocurement.tender.core.procedure.validation import validate_object_id_uniq


class CDStage1EUPostTender(PostTender):
    procurementMethodType = StringType(choices=[CD_EU_TYPE], default=CD_EU_TYPE)


class CDStage1EUPatchTender(PatchTender):
    procurementMethodType = StringType(choices=[CD_EU_TYPE])


class CDStage1EUTender(Tender):
    procurementMethodType = StringType(choices=[CD_EU_TYPE], required=True)

    stage2TenderID = StringType()  # TODO: move to a distinct endpoint


class CDStage1UAPostTender(CDStage1EUPostTender):
    procurementMethodType = StringType(choices=[CD_UA_TYPE], default=CD_UA_TYPE)


class CDStage1UAPatchTender(CDStage1EUPatchTender):
    procurementMethodType = StringType(choices=[CD_UA_TYPE])


class CDStage1UATender(CDStage1EUTender):
    procurementMethodType = StringType(choices=[CD_UA_TYPE], required=True)


class CDStage2LotId(Model):
    id = StringType()


class CDStage2Firm(Model):
    identifier = ModelType(Identifier, required=True)
    name = StringType(required=True)
    lots = ListType(ModelType(CDStage2LotId, required=True))


class CDStage2EUPostTender(PostTender):
    procurementMethodType = StringType(choices=[STAGE_2_EU_TYPE], default=STAGE_2_EU_TYPE)

    owner = StringType(required=True)
    tenderID = StringType()  # in tests it's not passed
    dialogue_token = StringType(required=True)
    dialogueID = StringType()
    shortlistedFirms = ListType(ModelType(CDStage2Firm, required=True), min_size=3, required=True)

    items = ListType(
        ModelType(CDItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )
    tenderPeriod = ModelType(PeriodEndRequired)

    criteria = ListType(
        ModelType(Criterion, required=True),
        validators=[validate_object_id_uniq, validate_criteria_requirement_uniq],
    )

    @serializable(serialized_name="tenderID")
    def serialize_tender_id(self):
        return self.tenderID  # just return what have been passed

    # Non-required mainProcurementCategory
    def validate_shortlistedFirms(self, data, value):
        validate_cd_shortlisted_firm_ids(data, value)


class CDStage2EUPatchTender(PatchTender):
    procurementMethodType = StringType(choices=[STAGE_2_EU_TYPE])

    items = ListType(
        ModelType(CDItem, required=True),
        min_size=1,
        validators=[validate_uniq_id],
    )


class CDStage2EUTender(Tender):
    procurementMethodType = StringType(choices=[STAGE_2_EU_TYPE], required=True)

    dialogue_token = StringType(required=True)
    dialogueID = StringType()

    items = ListType(
        ModelType(CDItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )
    shortlistedFirms = ListType(ModelType(CDStage2Firm, required=True), min_size=3, required=True)

    def validate_shortlistedFirms(self, data, value):
        validate_cd_shortlisted_firm_ids(data, value)


class CDStage2UAPostTender(CDStage2EUPostTender):
    procurementMethodType = StringType(choices=[STAGE_2_UA_TYPE], default=STAGE_2_UA_TYPE)


class CDStage2UAPatchTender(CDStage2EUPatchTender):
    procurementMethodType = StringType(choices=[STAGE_2_UA_TYPE])


class CDStage2UATender(CDStage2EUTender):
    procurementMethodType = StringType(choices=[STAGE_2_UA_TYPE], required=True)
