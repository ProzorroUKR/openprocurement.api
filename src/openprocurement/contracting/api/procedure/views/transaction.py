from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.transaction import ContractTransactionsResource


@resource(
    name="Contract transactions",
    path="/contracts/{contract_id}/transactions/{transaction_id}",
    contractType="general",
    description="Contract transactions",
)
class GeneralTransactionsResource(ContractTransactionsResource):
    pass
