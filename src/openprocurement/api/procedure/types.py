"""
Field types for pydantic models of the API (see models/base.py).
"""

import re
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from hashlib import algorithms_guaranteed
from hashlib import new as hash_new
from typing import Annotated, Any

from isodate import Duration, ISO8601Error, duration_isoformat, parse_duration
from pydantic import (
    AfterValidator,
    BeforeValidator,
    PlainSerializer,
)
from pydantic import PlainValidator as PydanticPlainValidator

from openprocurement.api.constants import TZ
from openprocurement.api.procedure.errors import ConversionError
from openprocurement.api.procedure.utils import parse_date

# --- datetime ---


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    try:
        return parse_date(value, default_timezone=TZ)
    except (ValueError, TypeError):
        raise ConversionError(f"Could not parse {value}. Should be ISO8601.")
    except OverflowError as e:
        raise ConversionError(str(e))


IsoDateTime = Annotated[
    datetime,
    PydanticPlainValidator(_parse_datetime),
    PlainSerializer(lambda value: value.isoformat(), return_type=str),
]


# --- strings ---


def validate_md5(value: str) -> str:
    if len(value) != 32:
        raise ConversionError("Hash value is wrong length.")
    try:
        int(value, 16)
    except ValueError:
        raise ConversionError("Hash value is not hexadecimal.")
    return value


MD5 = Annotated[str, AfterValidator(validate_md5)]


def _validate_hash(value: str) -> str:
    if ":" not in value:
        raise ConversionError("Hash type is not supported.")
    hash_type, hash_value = value.split(":", 1)
    if hash_type not in algorithms_guaranteed:
        raise ConversionError("Hash type is not supported.")
    if len(hash_value) != hash_new(hash_type).digest_size * 2:
        raise ConversionError("Hash value is wrong length.")
    try:
        int(hash_value, 16)
    except ValueError:
        raise ConversionError("Hash value is not hexadecimal.")
    return value


Hash = Annotated[str, AfterValidator(_validate_hash)]

URL_REGEX = re.compile(r"^https?://\S+$", re.IGNORECASE)


def _validate_url(value: str) -> str:
    if not URL_REGEX.match(value):
        raise ValueError("Not a well formed URL.")
    return value


Url = Annotated[str, AfterValidator(_validate_url)]

EMAIL_REGEX = re.compile(
    # dot-atom
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
    # quoted-string
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016'
    r'-\177])*"'
    # domain
    r")@(?:[A-Z0-9](?:[A-Z0-9-]{0,2000}[A-Z0-9])?\.)+[A-Z]{2,63}\.?$",
    re.IGNORECASE,
)


def _validate_email(value: str) -> str:
    if not EMAIL_REGEX.match(value):
        raise ValueError("Not a well formed email address.")
    return value


Email = Annotated[str, AfterValidator(_validate_email)]


# --- decimals ---


def _to_decimal(value: Any, precision: Decimal) -> Decimal:
    if isinstance(value, bool):
        raise ConversionError(f"Number '{value}' failed to convert to a decimal.")
    try:
        return Decimal(str(value) if isinstance(value, float) else value).quantize(precision, rounding=ROUND_HALF_UP)
    except (TypeError, ValueError, InvalidOperation):
        raise ConversionError(f"Number '{value}' failed to convert to a decimal.")


def DecimalOf(precision: int = -3) -> BeforeValidator:
    """`Annotated[Decimal, DecimalOf(-2)]`: the value is quantized (ROUND_HALF_UP) to the precision and normalized"""
    quant = Decimal(f"1E{precision:d}")

    def validate(value: Any) -> Decimal:
        result = _to_decimal(value, quant)
        if result.is_nan():
            raise ConversionError(f"Number '{value}' failed to convert to a decimal.")
        return result.normalize()

    return BeforeValidator(validate)


def NormalizedDecimalOf(precision: int = -3) -> BeforeValidator:
    """Like `DecimalOf`, but an integer value keeps one decimal place: 1 -> 1.0"""
    quant = Decimal(f"1E{precision:d}")

    def validate(value: Any) -> Decimal:
        result = _to_decimal(value, quant).normalize()
        if result == result.to_integral():
            return result.quantize(Decimal("0.1"))
        return result

    return BeforeValidator(validate)


def quantize(value: Any, precision: int) -> Decimal | None:
    """the output value of a computed field: quantized like `DecimalOf(precision)`"""
    if value is None:
        return None
    return _to_decimal(value, Decimal(f"1E{precision:d}")).normalize()


DecimalValue = Annotated[Decimal, DecimalOf(-3)]
NormalizedDecimal = Annotated[Decimal, NormalizedDecimalOf(-3)]
StringDecimal = Annotated[
    Decimal,
    DecimalOf(-3),
    PlainSerializer(lambda value: "{:f}".format(value), return_type=str),
]


# --- durations ---


def _parse_duration(value: Any) -> Duration | timedelta:
    if isinstance(value, (Duration, timedelta)):
        return value
    try:
        return parse_duration(value)
    except TypeError:
        raise ConversionError(f"Could not parse {value}. Should be ISO8601 Durations.")
    except ISO8601Error as e:
        raise ConversionError(str(e))


IsoDuration = Annotated[
    Any,
    PydanticPlainValidator(_parse_duration),
    PlainSerializer(duration_isoformat, return_type=str),
]
