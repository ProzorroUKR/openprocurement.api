# /home/andriis/ramki/openprocurement.buildout/src/openprocurement.tender.openeu/openprocurement/tender/openeu/models.py:610
from zope.component import getAdapter
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.api.adapters import Serializable
from openprocurement.tender.core.utils import calculate_business_date


class SerializableTenderEnquiryPeriod(Serializable):
    serialized_name = "enquiryPeriod"
    serialize_when_none = True

    def __call__(self, obj, *args, **kwargs):
        configurator = getAdapter(obj, IContentConfigurator)
        enquiryPeriod_class = obj._fields["enquiryPeriod"]
        endDate = calculate_business_date(obj.tenderPeriod.endDate, -configurator.questions_stand_still, obj)
        return enquiryPeriod_class(
            dict(
                startDate=obj.tenderPeriod.startDate,
                endDate=endDate,
                invalidationDate=obj.enquiryPeriod and obj.enquiryPeriod.invalidationDate,
                clarificationsUntil=calculate_business_date(endDate, configurator.enquiry_stand_still, obj, True),
            )
        )
