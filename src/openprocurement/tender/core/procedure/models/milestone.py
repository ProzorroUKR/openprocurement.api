from schematics.types import MD5Type, StringType
from openprocurement.api.models import IsoDateTimeType
from openprocurement.tender.core.procedure.context import get_tender, get_now
from openprocurement.tender.core.utils import calculate_tender_date, calculate_complaint_business_date
from schematics.exceptions import ValidationError
from schematics.types.serializable import serializable
from openprocurement.tender.core.procedure.models.base import Model, ModelType, ListType
from datetime import timedelta
from uuid import uuid4


class QualificationMilestone(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    CODE_24_HOURS = "24h"
    CODE_LOW_PRICE = "alp"
    code = StringType(required=True, choices=[CODE_24_HOURS, CODE_LOW_PRICE])
    dueDate = IsoDateTimeType()
    description = StringType()
    date = IsoDateTimeType(default=get_now)

    # class Options:
    #     namespace = "Milestone"
    #     roles = {
    #         "create": whitelist("code", "description"),
    #         "Administrator": whitelist("dueDate"),
    #         "view": schematics_default_role,
    #     }

    @serializable(serialized_name="dueDate")
    def set_due_date(self):
        if not self.dueDate:
            if self.code == self.CODE_24_HOURS:
                self.dueDate = calculate_tender_date(
                    self.date, timedelta(hours=24), get_tender()
                )
            elif self.code == self.CODE_LOW_PRICE:
                self.dueDate = calculate_complaint_business_date(
                    self.date, timedelta(days=1), get_tender(), working_days=True
                )
        return self.dueDate and self.dueDate.isoformat()


class QualificationMilestoneListMixin(Model):
    milestones = ListType(ModelType(QualificationMilestone, required=True), default=list)

    def validate_milestones(self, data, milestones):
        """
        This validation on the model, not on the view
        because there is a way to post milestone to different zones (couchdb masters)
        and concord will merge them, that shouldn't be the case
        """
        if len(list([m for m in milestones if m.code == QualificationMilestone.CODE_24_HOURS])) > 1:
            raise ValidationError("There can be only one '24h' milestone")
