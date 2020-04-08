from openprocurement.tender.core.models import BaseCancellation


# TODO: relatedLot
class Cancellation(BaseCancellation):
    def validate_relatedLot(self, data, relatedLot):
        pass
