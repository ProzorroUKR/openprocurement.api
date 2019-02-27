from openprocurement.api.adapters import Serializable


class SerializableAgreementNumberOfContracts(Serializable):
    serialized_name = "numberOfContracts"

    def __call__(self, obj, *args, **kwargs):
        return len([c.id for c in obj.contracts if c.status == 'active'])
