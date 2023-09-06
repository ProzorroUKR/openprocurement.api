from logging import getLogger

from openprocurement.contracting.core.procedure.state.contract import BaseContractState

LOGGER = getLogger(__name__)


class ContractState(BaseContractState):
    terminated_statuses = ("terminated",)
