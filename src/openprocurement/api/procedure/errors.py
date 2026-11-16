"""
Errors of the API models and the conversion of pydantic errors to the structure of the API errors:

    {"budget": {"breakdown": [{"title": ["This field is required."]}]}, "foo": "Rogue field"}

The data is validated in two steps: conversion errors (wrong types, unknown fields) hide the validation ones
(required, choices, limits, etc.).
"""

import ast
import re
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable

from pydantic import ValidationError as PydanticValidationError
from pydantic_core import ErrorDetails

REQUIRED_MESSAGE = "This field is required."
ROGUE_FIELD_MESSAGE = "Rogue field"


# --- exceptions ---


class ValidationError(ValueError):
    """
    A validation error of the data, raised by validators of models and states.
    `messages` is a list of messages or a structure of them (a dict by fields, a list by items).
    """

    def __init__(self, messages: Any):
        if not isinstance(messages, (list, tuple, dict)):
            messages = [messages]
        if isinstance(messages, dict):
            messages = {key: _messages_of(value) for key, value in messages.items()}
        else:
            messages = [_messages_of(value) for value in messages]
        super().__init__(messages)
        self.messages = messages


def _messages_of(value: Any) -> Any:
    return value.messages if isinstance(value, ValidationError) else value


class ConversionError(ValidationError):
    """
    The input value can't be converted to the type of the field.
    Conversion errors are reported apart from the validation ones, see `api_errors`.
    """


class DataValidationError(ValidationError):
    """Raised by `Model.validate_data`, `messages` have the structure of the API errors (see `api_errors`)."""


class FieldError(ValueError):
    """
    An error of a model level validation that belongs to a field:

        @model_validator(mode="after")
        def validate_dates(self):
            if self.startDate and self.endDate and self.endDate < self.startDate:
                raise FieldError("startDate", "period should begin before its end")
            return self
    """

    def __init__(self, field: str, message: Any):
        super().__init__(message)
        self.field = field
        self.message = message

    @property
    def messages(self) -> Any:
        return [self.message] if isinstance(self.message, str) else self.message


class FieldErrors(ValueError):
    """Several errors of a model level validation: `raise FieldErrors({"name": "...", "name_en": "..."})`"""

    def __init__(self, messages: dict[str, str]):
        super().__init__(messages)
        self.errors = [FieldError(field, message) for field, message in messages.items()]


@contextmanager
def field_error(field: str):
    """
    Attaches errors of a model level validation to a field:

        @model_validator(mode="after")
        def validate_value(self):
            with field_error("value"):
                validate_lot_value(self.value, self.relatedLot)
            return self
    """
    try:
        yield
    except FieldError:
        raise
    except ValidationError as e:
        raise FieldError(field, e.messages)
    except ValueError as e:
        raise FieldError(field, str(e))


# --- tags of discriminated unions (pydantic puts them into the error locations) ---

# {field name: tags}
_union_tags: dict[str, set[str]] = {}


def register_union_tags(names: set[str], tags: set[str]) -> None:
    """The tags of the discriminated unions of a field (by its input and output names), see `Model`"""
    for name in names:
        _union_tags.setdefault(name, set()).update(tags)


def without_union_tags(loc: tuple) -> tuple:
    """`("changes", 0, "taxRate", "modifications")` -> `("changes", 0, "modifications")`"""
    result: list = []
    field = None
    for key in loc:
        if isinstance(key, str):
            if field is not None and key in _union_tags.get(field, ()):
                field = None
                continue
            field = key
        result.append(key)
    return tuple(result)


# --- one pydantic error -> API messages ---


@dataclass(frozen=True)
class Translated:
    messages: Any  # a list of messages, "Rogue field" or a structure of messages
    conversion: bool = False  # conversion errors hide the validation ones
    extra_loc: tuple = ()  # `FieldError` attaches the error to a field of the model


Translator = Callable[[ErrorDetails], Translated]


def _ctx(error: ErrorDetails) -> dict[str, Any]:
    return error.get("ctx") or {}


def _number_type(value: Any) -> str:
    return type(value).__name__.capitalize()


def _number(value: Any) -> Any:
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _items(count: int) -> str:
    return f"{count} item" if count == 1 else f"{count} items"


def _limit(value: Any) -> Any:
    # a constraint of an optional decimal field comes as "Decimal('0.99')"
    if isinstance(value, str) and value.startswith("Decimal('") and value.endswith("')"):
        return Decimal(value[len("Decimal('") : -2])
    return value


def expected_choices(expected: str) -> list:
    """
    The choices of a `Literal` / enum field from the pydantic error context:
    "'draft', 'active' or 'complete'", "<Kind.GENERAL: 'general'> or <Kind.OTHER: 'other'>"
    """
    expected = re.sub(r"<[\w.]+: (.+?)>(?=, <| or <|$)", r"\1", expected)
    candidates = [expected]
    position = expected.rfind(" or ")
    while position != -1:  # " or " joins the last two choices (it can be a part of a choice as well)
        candidates.append(f"{expected[:position]}, {expected[position + 4 :]}")
        position = expected.rfind(" or ", 0, position)
    for candidate in candidates:
        try:
            return list(ast.literal_eval(f"[{candidate}]"))
        except (ValueError, SyntaxError):
            continue
    return [expected]


def _required(error: ErrorDetails) -> Translated:
    return Translated([REQUIRED_MESSAGE])


def _rogue(error: ErrorDetails) -> Translated:
    return Translated(ROGUE_FIELD_MESSAGE, conversion=True)


def _custom(error: ErrorDetails) -> Translated:
    """an error raised by a validator of the model"""
    exc = _ctx(error).get("error")
    if isinstance(exc, FieldError):
        return Translated(exc.messages, extra_loc=(exc.field,))
    if isinstance(exc, ValidationError):
        return Translated(exc.messages, conversion=isinstance(exc, ConversionError))
    return Translated([str(exc)])


def _not_string(error: ErrorDetails) -> Translated:
    return Translated([f"Couldn't interpret '{error.get('input')}' as string."], conversion=True)


def _choices(error: ErrorDetails) -> Translated:
    # NOTE: python caches `Literal[...] | None`: literals with the same values in a different order
    # share the order of the first one defined, keep one order of the same choices in the models
    choices = expected_choices(_ctx(error).get("expected", ""))
    if not isinstance(error.get("input"), str) and all(isinstance(choice, str) for choice in choices):
        return _not_string(error)
    return Translated([f"Value must be one of {choices}."])


def _message(message: str) -> Translator:
    return lambda error: Translated([message])


def _not_float(error: ErrorDetails) -> Translated:
    return Translated([f"Value '{error.get('input')}' is not float."], conversion=True)


def _not_int(error: ErrorDetails) -> Translated:
    return Translated([f"Value '{error.get('input')}' is not int."], conversion=True)


def _not_bool(error: ErrorDetails) -> Translated:
    return Translated(["Must be either true or false."], conversion=True)


def _greater_than(error: ErrorDetails) -> Translated:
    limit = _limit(_ctx(error).get("ge", _ctx(error).get("gt")))
    if isinstance(limit, Decimal):
        return Translated([f"Value should be greater than {limit}."])
    return Translated([f"{_number_type(limit)} value should be greater than {_number(limit)}."])


def _less_than(error: ErrorDetails) -> Translated:
    limit = _limit(_ctx(error).get("le", _ctx(error).get("lt")))
    if isinstance(limit, Decimal):
        return Translated([f"Value should be less than {limit}."])
    return Translated([f"{_number_type(limit)} value should be less than {_number(limit)}."])


def _too_short(error: ErrorDetails) -> Translated:
    return Translated([f"Please provide at least {_items(_ctx(error)['min_length'])}."])


def _too_long(error: ErrorDetails) -> Translated:
    return Translated([f"Please provide no more than {_items(_ctx(error)['max_length'])}."])


def _not_mapping(error: ErrorDetails) -> Translated:
    class_name = _ctx(error).get("class_name", "dict")
    value_type = type(error.get("input")).__name__
    return Translated([f"Please use a mapping for this field or {class_name} instance instead of {value_type}."], True)


# pydantic error type -> API messages
TRANSLATORS: dict[str, Translator] = {
    "missing": _required,
    "extra_forbidden": _rogue,
    "value_error": _custom,
    "assertion_error": _custom,
    "literal_error": _choices,
    "enum": _choices,
    "string_type": _not_string,
    "string_too_long": _message("String value is too long."),
    "string_too_short": _message("String value is too short."),
    "string_pattern_mismatch": _message("String value did not match validation regex."),
    "float_type": _not_float,
    "float_parsing": _not_float,
    "finite_number": _not_float,
    "int_type": _not_int,
    "int_parsing": _not_int,
    "int_from_float": _not_int,
    "int_parsing_size": _not_int,
    "bool_type": _not_bool,
    "bool_parsing": _not_bool,
    "greater_than": _greater_than,
    "greater_than_equal": _greater_than,
    "less_than": _less_than,
    "less_than_equal": _less_than,
    "too_short": _too_short,
    "too_long": _too_long,
    "model_type": _not_mapping,
    "model_attributes_type": _not_mapping,
    "dict_type": _not_mapping,
}


def translate(error: ErrorDetails) -> Translated:
    """One pydantic error (an item of `ValidationError.errors()`) -> API messages"""
    error_type = error["type"]
    if error.get("input") is None and error_type.endswith("_type"):
        return _required(error)  # `null` for a field that can't be `null`
    translator = TRANSLATORS.get(error_type)
    if translator is None:  # not mapped: the pydantic message as is
        return Translated([error["msg"]], conversion=error_type.endswith(("_type", "_parsing")))
    return translator(error)


# --- all the errors -> the structure of the API errors ---


class _Leaf:
    def __init__(self):
        self.messages: Any = []

    def add(self, messages: Any):
        if isinstance(messages, list) and isinstance(self.messages, list):
            self.messages.extend(messages)
        else:  # "Rogue field" or a structure of messages
            self.messages = messages


def _build(node: Any, conversion: bool) -> Any:
    if isinstance(node, _Leaf):
        return node.messages
    leaf = node.get(())
    if leaf is not None:  # an error of the object itself hides the errors of its parts
        return leaf.messages
    indexes = sorted(key for key in node if isinstance(key, int))
    if indexes:
        if conversion:  # only the first item that failed to convert is reported
            return _build(node[indexes[0]], conversion)
        return [_build(node[index], conversion) for index in indexes]  # only the items with errors
    built = {key: _build(child, conversion) for key, child in node.items()}
    # the unknown fields of an object are reported before the errors of its fields
    rogue = {key: messages for key, messages in built.items() if messages == ROGUE_FIELD_MESSAGE}
    return {**rogue, **{key: messages for key, messages in built.items() if key not in rogue}}


def api_errors(exc: PydanticValidationError) -> Any:
    """Converts pydantic errors to the structure of the API errors (see the module docstring)"""
    errors = []
    for error in exc.errors(include_url=False):
        cause = _ctx(error).get("error")
        if isinstance(cause, FieldErrors):
            for error_of_field in cause.errors:
                errors.append((tuple(error["loc"]) + (error_of_field.field,), error_of_field.messages, False))
            continue
        translated = translate(error)
        loc = without_union_tags(error["loc"])
        errors.append((loc + translated.extra_loc, translated.messages, translated.conversion))

    has_conversion_errors = any(conversion for _, _, conversion in errors)
    if has_conversion_errors:
        errors = [error for error in errors if error[2]]

    root: dict = {}
    for loc, messages, _ in errors:
        node: Any = root
        for key in loc:
            node = node.setdefault(key, {})
            if isinstance(node, _Leaf):
                break
        if isinstance(node, dict):
            node = node.setdefault((), _Leaf())
        node.add(messages)

    return _build(root, has_conversion_errors)
