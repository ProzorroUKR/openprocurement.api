from schematics.exceptions import ValidationError


class TenderPeriodValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, period):
        if period and period.startDate and data.get('enquiryPeriod') and data.get(
                'enquiryPeriod').endDate and period.startDate < data.get('enquiryPeriod').endDate:
            raise ValidationError(u"period should begin after enquiryPeriod")
