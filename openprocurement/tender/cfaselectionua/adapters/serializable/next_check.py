from zope.component import getAdapter

from openprocurement.api.adapters import Serializable
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.api.utils import get_now
from openprocurement.tender.core.utils import (
    calc_auction_end_time,
)


class SerializableTenderNextCheck(Serializable):
    serialized_name = "next_check"
    serialize_when_none = False

    def __call__(self, obj):
        now = get_now()
        checks = []
        configurator = getAdapter(obj, IContentConfigurator)
        if obj.status == 'active.enquiries' and obj.tenderPeriod.startDate:
            checks.append(obj.tenderPeriod.startDate.astimezone(configurator.tz))
        elif obj.status == 'active.enquiries' and obj.enquiryPeriod.endDate:
            checks.append(obj.enquiryPeriod.endDate.astimezone(configurator.tz))
        elif obj.status == 'active.tendering' and obj.tenderPeriod.endDate:
            checks.append(obj.tenderPeriod.endDate.astimezone(configurator.tz))
        elif not obj.lots and obj.status == 'active.auction' and obj.auctionPeriod and obj.auctionPeriod.startDate and not obj.auctionPeriod.endDate:
            if now < obj.auctionPeriod.startDate:
                checks.append(obj.auctionPeriod.startDate.astimezone(configurator.tz))
            elif now < calc_auction_end_time(obj.numberOfBids, obj.auctionPeriod.startDate).astimezone(
                    configurator.tz):
                checks.append(
                    calc_auction_end_time(obj.numberOfBids, obj.auctionPeriod.startDate).astimezone(configurator.tz))
        elif obj.lots and obj.status == 'active.auction':
            for lot in obj.lots:
                if lot.status != 'active' or not lot.auctionPeriod or not lot.auctionPeriod.startDate or lot.auctionPeriod.endDate:
                    continue
                if now < lot.auctionPeriod.startDate:
                    checks.append(lot.auctionPeriod.startDate.astimezone(configurator.tz))
                elif now < calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(
                        configurator.tz):
                    checks.append(calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(
                        configurator.tz))
        elif obj.lots and obj.status in ['active.qualification', 'active.awarded']:
            for lot in obj.lots:
                if lot['status'] != 'active':
                    continue
        if obj.status.startswith('active'):
            for award in obj.awards:
                if award.status == 'active' and not any([i.awardID == award.id for i in obj.contracts]):
                    checks.append(award.date)
        return min(checks).isoformat() if checks else None
