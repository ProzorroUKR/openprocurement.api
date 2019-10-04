from schematics.exceptions import ValidationError


class TenderAwardPeriodValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, period):
        if (
            period
            and period.startDate
            and data.get("auctionPeriod")
            and data.get("auctionPeriod").endDate
            and period.startDate < data.get("auctionPeriod").endDate
        ):
            raise ValidationError(u"period should begin after auctionPeriod")
        if (
            period
            and period.startDate
            and data.get("tenderPeriod")
            and data.get("tenderPeriod").endDate
            and period.startDate < data.get("tenderPeriod").endDate
        ):
            raise ValidationError(u"period should begin after tenderPeriod")
