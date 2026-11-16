"""
Converters of values by a data type name (`dataType` of criteria requirements and their responses).
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

from openprocurement.api.procedure.errors import ConversionError

DATETIME_FORMATS = (
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
)


def to_string(value: Any) -> str | None:
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    raise ConversionError(f"Couldn't interpret '{value}' as string.")


def to_integer(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ConversionError(f"Value '{value}' is not int.")


def to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(value if isinstance(value, str) else str(value))
    except (TypeError, InvalidOperation):
        raise ConversionError(f"Number '{value}' failed to convert to a decimal.")


def to_boolean(value: Any) -> bool:
    if isinstance(value, str):
        if value in ("True", "true", "1"):
            value = True
        elif value in ("False", "false", "0"):
            value = False
    if isinstance(value, int) and value in [0, 1]:
        value = bool(value)
    if not isinstance(value, bool):
        raise ConversionError("Must be either true or false.")
    return value


def to_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    raise ConversionError(f"Could not parse {value}. Should be ISO8601.")


TYPEMAP: dict[str, Callable[[Any], Any]] = {
    "string": to_string,
    "integer": to_integer,
    "number": to_decimal,
    "boolean": to_boolean,
    "date-time": to_datetime,
}
