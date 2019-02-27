from barbecue import vnmax
from schematics.exceptions import ValidationError


class TenderFeaturesValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, features):
        if features and data['lots'] and any([
            round(vnmax([
                i
                for i in features
                if i.featureOf == 'tenderer' or i.featureOf == 'lot' and i.relatedItem == lot['id'] or
                                        i.featureOf == 'item' and
                                        i.relatedItem in [j.id for j in data['items'] if j.relatedLot == lot['id']]
            ]), 15) > 0.3
            for lot in data['lots']
        ]):
            raise ValidationError(u"Sum of max value of all features for lot should be less then or equal to 30%")
        elif features and not data['lots'] and round(vnmax(features), 15) > 0.3:
            raise ValidationError(u"Sum of max value of all features should be less then or equal to 30%")
