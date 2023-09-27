from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.transaction import ContractTransactionsResource


@resource(
    name="EContract transactions",
    path="/contracts/{contract_id}/transactions/{transaction_id}",
    contractType="econtract",
    description="EContract transactions",
)
class GeneralTransactionsResource(ContractTransactionsResource):
    pass
