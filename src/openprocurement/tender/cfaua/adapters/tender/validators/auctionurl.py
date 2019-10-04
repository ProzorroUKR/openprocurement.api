from schematics.exceptions import ValidationError


class TenderAuctionUrlValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, url):
        if url and data["lots"]:
            raise ValidationError(u"url should be posted for each lot")
