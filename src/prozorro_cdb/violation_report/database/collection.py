import logging

from prozorro_cdb.api.database.store import BaseCollection

logger = logging.getLogger(__name__)


class ViolationReportCollection(BaseCollection):
    object_name = "violation_report"
    collection_name = "open_violation_reports"
