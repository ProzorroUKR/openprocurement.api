from openprocurement.api.models import read_json
from openprocurement.api.utils import ACCELERATOR_RE, timedelta, datetime, time

WORKING_DAYS = read_json('working_days.json')


def calculate_business_date(date_obj, timedelta_obj, context=None, working_days=False):
    if context and 'procurementMethodDetails' in context and context['procurementMethodDetails']:
        re_obj = ACCELERATOR_RE.search(context['procurementMethodDetails'])
        if re_obj and 'accelerator' in re_obj.groupdict():
            return date_obj + (timedelta_obj / int(re_obj.groupdict()['accelerator']))
    if working_days:
        date = date_obj
        if timedelta_obj > timedelta():
            if date_obj.weekday() in [5, 6] and WORKING_DAYS.get(date_obj.date().isoformat(), True) or WORKING_DAYS.get(date_obj.date().isoformat(), False):
                date_obj = datetime.combine(date_obj.date(), time(0, tzinfo=date_obj.tzinfo)) + timedelta(1)
                while date_obj.weekday() in [5, 6] and WORKING_DAYS.get(date_obj.date().isoformat(), True) or WORKING_DAYS.get(date_obj.date().isoformat(), False):
                    date_obj += timedelta(1)
        else:
            if date_obj.weekday() in [5, 6] and WORKING_DAYS.get(date_obj.date().isoformat(), True) or WORKING_DAYS.get(date_obj.date().isoformat(), False):
                date_obj = datetime.combine(date_obj.date(), time(0, tzinfo=date_obj.tzinfo))
                while date_obj.weekday() in [5, 6] and WORKING_DAYS.get(date_obj.date().isoformat(), True) or WORKING_DAYS.get(date_obj.date().isoformat(), False):
                    date_obj -= timedelta(1)
                date_obj += timedelta(1)
        for _ in xrange(abs(timedelta_obj.days)):
            date_obj += timedelta(1) if timedelta_obj > timedelta() else -timedelta(1)
            while date_obj.weekday() in [5, 6] and WORKING_DAYS.get(date_obj.date().isoformat(), True) or WORKING_DAYS.get(date_obj.date().isoformat(), False):
                date_obj += timedelta(1) if timedelta_obj > timedelta() else -timedelta(1)
        return date_obj
    return date_obj + timedelta_obj
