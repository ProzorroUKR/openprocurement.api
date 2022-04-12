from openprocurement.tender.core.procedure.models.item import Item as BaseItem


class Item(BaseItem):
    def validate_unit(self, data, value):
        pass

    def validate_quantity(self, data, value):
        pass
