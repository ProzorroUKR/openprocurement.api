# /home/andriis/ramki/openprocurement.buildout/src/openprocurement.tender.openeu/openprocurement/tender/openeu/models.py:610
from zope.component import getAdapter
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.api.adapters import Serializable
from openprocurement.tender.core.utils import calculate_tender_business_date, calculate_clarif_business_date


class SerializableTenderEnquiryPeriod(Serializable):
    serialized_name = "enquiryPeriod"
    serialize_when_none = True

    def __call__(self, obj, *args, **kwargs):
        configurator = getAdapter(obj, IContentConfigurator)
        enquiry_period_class = obj._fields["enquiryPeriod"]
        end_date = calculate_tender_business_date(obj.tenderPeriod.endDate, -configurator.questions_stand_still, obj)
        clarifications_until = calculate_clarif_business_date(end_date, configurator.enquiry_stand_still, obj, True)
        return enquiry_period_class(
            dict(
                startDate=obj.tenderPeriod.startDate,
                endDate=end_date,
                invalidationDate=obj.enquiryPeriod and obj.enquiryPeriod.invalidationDate,
                clarificationsUntil=clarifications_until,
            )
        )
