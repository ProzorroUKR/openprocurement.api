import re
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from hashlib import algorithms_guaranteed
from hashlib import new as hash_new

from isodate import Duration, ISO8601Error, duration_isoformat, parse_duration
from schematics.exceptions import ConversionError, StopValidation, ValidationError
from schematics.types import BaseType
from schematics.types import DecimalType as BaseDecimalType
from schematics.types import StringType
from schematics.types.compound import ListType as BaseListType
from schematics.types.compound import ModelType as BaseModelType

from openprocurement.api.constants import TZ
from openprocurement.api.procedure.utils import parse_date


class ListType(BaseListType):
    # TODO: RM
    pass


class ModelType(BaseModelType):
    # TODO: RM
    pass


class DecimalType(BaseDecimalType):
    def __init__(self, precision=-3, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value, self.max_value = min_value, max_value
        self.precision = Decimal("1E{:d}".format(precision))

    def _apply_precision(self, value):
        try:
            value = Decimal(value).quantize(self.precision, rounding=ROUND_HALF_UP).normalize()
        except (TypeError, InvalidOperation):
            raise ConversionError(self.messages["number_coerce"].format(value))
        return value

    def to_primitive(self, value, context=None):
        return self._apply_precision(value)

    def to_native(self, value, context=None):
        return self._apply_precision(value)


class StringDecimalType(BaseDecimalType):
    def to_primitive(self, *args, **kwargs):
        value = super().to_primitive(*args, **kwargs)
        if isinstance(value, Decimal):
            return '{:f}'.format(value)
        return value


class URLType(StringType):
    # TODO: remove custom URLType after newer version of schematics will be used. The latest version has universal regex.

    MESSAGES = {
        'invalid_url': "Not a well formed URL.",
    }

    URL_REGEX = re.compile(r'^https?://\S+$', re.IGNORECASE)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def validate_url(self, value):
        if not URLType.URL_REGEX.match(value):
            raise StopValidation(self.messages['invalid_url'])


class IsoDateTimeType(BaseType):
    MESSAGES = {"parse": "Could not parse {0}. Should be ISO8601."}

    def to_native(self, value, context=None):
        if isinstance(value, datetime):
            return value
        try:
            return parse_date(value, default_timezone=TZ)
        except ValueError:
            raise ConversionError(self.messages["parse"].format(value))
        except OverflowError as e:
            raise ConversionError(str(e))

    def to_primitive(self, value, context=None):
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class IsoDurationType(BaseType):
    """Iso Duration format
    P is the duration designator (referred to as "period"), and is always placed at the beginning of the duration.
    Y is the year designator that follows the value for the number of years.
    M is the month designator that follows the value for the number of months.
    W is the week designator that follows the value for the number of weeks.
    D is the day designator that follows the value for the number of days.
    T is the time designator that precedes the time components.
    H is the hour designator that follows the value for the number of hours.
    M is the minute designator that follows the value for the number of minutes.
    S is the second designator that follows the value for the number of seconds.
    examples:  'P5000Y72M8W10DT55H3000M5S'
    """

    MESSAGES = {"parse": "Could not parse {0}. Should be ISO8601 Durations."}

    def to_native(self, value, context=None):
        if isinstance(value, Duration) or isinstance(value, timedelta):
            return value
        try:
            return parse_duration(value)
        except TypeError:
            raise ConversionError(self.messages["parse"].format(value))
        except ISO8601Error as e:
            raise ConversionError(str(e))

    def to_primitive(self, value, context=None):
        return duration_isoformat(value)


class HashType(StringType):
    MESSAGES = {
        "hash_invalid": "Hash type is not supported.",
        "hash_length": "Hash value is wrong length.",
        "hash_hex": "Hash value is not hexadecimal.",
    }

    def to_native(self, value, context=None):
        value = super().to_native(value, context)

        if ":" not in value:
            raise ValidationError(self.messages["hash_invalid"])

        hash_type, hash_value = value.split(":", 1)

        if hash_type not in algorithms_guaranteed:
            raise ValidationError(self.messages["hash_invalid"])

        if len(hash_value) != hash_new(hash_type).digest_size * 2:
            raise ValidationError(self.messages["hash_length"])
        try:
            int(hash_value, 16)
        except ValueError:
            raise ConversionError(self.messages["hash_hex"])
        return value
