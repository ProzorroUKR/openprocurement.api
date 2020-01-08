
from openprocurement.tender.core.utils import check_cancellation_status


def check_status(request):
    check_cancellation_status(request)
