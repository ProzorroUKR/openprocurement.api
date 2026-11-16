from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal

import pytest
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic import ValidationError as PydanticValidationError

from openprocurement.api.procedure.errors import (
    TRANSLATORS,
    ConversionError,
    FieldError,
    FieldErrors,
    ValidationError,
    api_errors,
    expected_choices,
    field_error,
    register_union_tags,
    translate,
    without_union_tags,
)


class Kind(StrEnum):
    GENERAL = "general"
    OTHER = "other"


class Sample(BaseModel):
    model_config = ConfigDict(extra="forbid", regex_engine="python-re")

    title: str | None = Field(None, min_length=2, max_length=3, pattern=r"\d+")
    count: int | None = Field(None, ge=0, le=10)
    amount: float | None = Field(None, gt=0.5)
    rate: float | None = None
    finite: float | None = Field(None, allow_inf_nan=False)
    share: Decimal | None = Field(None, ge=Decimal("0.0"), le=Decimal("0.99"))
    flag: bool | None = None
    status: Literal["draft", "active"] | None = None
    kind: Kind | None = None
    tags: list[str] | None = Field(None, min_length=1, max_length=2)
    mapping: dict[str, str] | None = None
    child: "Sample | None" = None


class Required(BaseModel):
    title: str


class Custom(BaseModel):
    value: int | None = None

    @model_validator(mode="after")
    def check(self):
        if self.value == 1:
            raise ValueError("plain error")
        if self.value == 2:
            raise ValidationError(["validation error"])
        if self.value == 3:
            raise ConversionError("conversion error")
        if self.value == 4:
            raise FieldError("value", "field error")
        if self.value == 5:
            raise FieldErrors({"value": "first", "other": "second"})
        if self.value == 6:
            with field_error("value"):
                raise ValueError("attached error")
        return self


class Asserted(BaseModel):
    value: int | None = None

    @model_validator(mode="after")
    def check(self):
        if self.value == 1:
            # `raise` instead of `assert`: pytest rewrites the messages of `assert` in the test modules
            raise AssertionError("assertion error")
        return self


def pydantic_errors(model: type[BaseModel], data: dict) -> list:
    with pytest.raises(PydanticValidationError) as e:
        model.model_validate(data)
    return e.value.errors(include_url=False)


def validation_error(model: type[BaseModel], data: dict) -> PydanticValidationError:
    with pytest.raises(PydanticValidationError) as e:
        model.model_validate(data)
    return e.value


# one case per translated pydantic error type: (error type, model, input, API messages, conversion error);
# the cases without a model are checked by their own tests
CASES = [
    ("missing", Required, {}, ["This field is required."], False),
    ("extra_forbidden", Sample, {"foo": 1}, "Rogue field", True),
    ("value_error", Custom, {"value": 1}, ["plain error"], False),
    ("assertion_error", Asserted, {"value": 1}, ["assertion error"], False),
    ("literal_error", Sample, {"status": "x"}, ["Value must be one of ['draft', 'active']."], False),
    ("enum", Sample, {"kind": "x"}, ["Value must be one of ['general', 'other']."], False),
    ("string_type", Sample, {"title": 1}, ["Couldn't interpret '1' as string."], True),
    ("string_too_long", Sample, {"title": "1234"}, ["String value is too long."], False),
    ("string_too_short", Sample, {"title": "1"}, ["String value is too short."], False),
    ("string_pattern_mismatch", Sample, {"title": "ab"}, ["String value did not match validation regex."], False),
    ("float_type", Sample, {"rate": [1]}, ["Value '[1]' is not float."], True),
    ("float_parsing", Sample, {"rate": "x"}, ["Value 'x' is not float."], True),
    ("finite_number", Sample, {"finite": float("inf")}, ["Value 'inf' is not float."], True),
    ("int_type", Sample, {"count": [1]}, ["Value '[1]' is not int."], True),
    ("int_parsing", Sample, {"count": "x"}, ["Value 'x' is not int."], True),
    ("int_from_float", Sample, {"count": 1.5}, ["Value '1.5' is not int."], True),
    ("int_parsing_size", Sample, {"count": "9" * 5000}, [f"Value '{'9' * 5000}' is not int."], True),
    ("bool_type", Sample, {"flag": [1]}, ["Must be either true or false."], True),
    ("bool_parsing", Sample, {"flag": "x"}, ["Must be either true or false."], True),
    ("greater_than", Sample, {"amount": 0.5}, ["Float value should be greater than 0.5."], False),
    ("greater_than_equal", Sample, {"count": -1}, ["Int value should be greater than 0."], False),
    ("less_than", None, None, None, False),  # see test_less_than
    ("less_than_equal", Sample, {"count": 11}, ["Int value should be less than 10."], False),
    ("too_short", Sample, {"tags": []}, ["Please provide at least 1 item."], False),
    ("too_long", Sample, {"tags": ["a", "b", "c"]}, ["Please provide no more than 2 items."], False),
    (
        "model_type",
        Sample,
        {"child": "x"},
        ["Please use a mapping for this field or Sample instance instead of str."],
        True,
    ),
    ("model_attributes_type", None, None, None, True),  # see test_model_attributes_type
    (
        "dict_type",
        Sample,
        {"mapping": "x"},
        ["Please use a mapping for this field or dict instance instead of str."],
        True,
    ),
]


TRANSLATE_CASES = [case for case in CASES if case[1] is not None]


@pytest.mark.parametrize(
    "error_type, model, data, messages, conversion",
    TRANSLATE_CASES,
    ids=[f"{case[0]}-{i}" for i, case in enumerate(TRANSLATE_CASES)],
)
def test_translate(error_type, model, data, messages, conversion):
    (error,) = pydantic_errors(model, data)
    assert error["type"] == error_type  # pydantic still reports this type for the input
    translated = translate(error)
    assert translated.messages == messages
    assert translated.conversion is conversion


def test_every_translator_has_a_case():
    assert set(TRANSLATORS) == {case[0] for case in CASES}


def test_decimal_limits():
    (error,) = pydantic_errors(Sample, {"share": "1"})
    assert error["type"] == "less_than_equal"
    assert translate(error).messages == ["Value should be less than 0.99."]
    (error,) = pydantic_errors(Sample, {"share": "-1"})
    assert translate(error).messages == ["Value should be greater than 0.0."]


def test_less_than():
    class Limited(BaseModel):
        value: int = Field(lt=10)

    (error,) = pydantic_errors(Limited, {"value": 10})
    assert error["type"] == "less_than"
    assert translate(error).messages == ["Int value should be less than 10."]


def test_model_attributes_type():
    # pydantic reports it for an object that is not a mapping in the `from_attributes` mode
    error = {
        "type": "model_attributes_type",
        "loc": ("child",),
        "msg": "...",
        "input": 1,
        "ctx": {"class_name": "Child"},
    }
    translated = translate(error)
    assert translated.messages == ["Please use a mapping for this field or Child instance instead of int."]
    assert translated.conversion is True


def test_null_for_not_nullable_field():
    (error,) = pydantic_errors(Required, {"title": None})
    assert error["type"] == "string_type"
    assert translate(error).messages == ["This field is required."]
    assert translate(error).conversion is False


def test_choices_of_not_string_input():
    (error,) = pydantic_errors(Sample, {"status": 1})
    assert translate(error).messages == ["Couldn't interpret '1' as string."]
    assert translate(error).conversion is True


def test_not_translated_error_keeps_pydantic_message():
    error = {"type": "url_parsing", "loc": ("x",), "msg": "Input should be a valid URL", "input": "x"}
    assert translate(error).messages == ["Input should be a valid URL"]
    assert translate(error).conversion is True
    error = {"type": "date_from_datetime_inexact", "loc": ("x",), "msg": "Datetimes provided ...", "input": "x"}
    assert translate(error).conversion is False


# --- the errors raised by validators ---


@pytest.mark.parametrize(
    "value, errors",
    [
        (2, ["validation error"]),
        (3, ["conversion error"]),
        (4, {"value": ["field error"]}),
        (5, {"value": ["first"], "other": ["second"]}),
        (6, {"value": ["attached error"]}),
    ],
)
def test_validator_errors(value, errors):
    assert api_errors(validation_error(Custom, {"value": value})) == errors


def test_conversion_error_of_validator_hides_validation_errors():
    class Model(BaseModel):
        value: int | None = None
        other: int | None = Field(None, ge=0)

        @model_validator(mode="before")
        @classmethod
        def check(cls, data):
            if data.get("value") == 1:
                raise ConversionError("conversion error")
            return data

    assert api_errors(validation_error(Model, {"value": 1, "other": -1})) == ["conversion error"]


def test_validation_error_messages():
    assert ValidationError("message").messages == ["message"]
    assert ValidationError(["a", ValidationError("b")]).messages == ["a", ["b"]]
    assert ValidationError({"field": ValidationError("b")}).messages == {"field": ["b"]}


# --- the structure of the errors ---


def test_nested_errors():
    assert api_errors(validation_error(Sample, {"child": {"count": -1}})) == {
        "child": {"count": ["Int value should be greater than 0."]}
    }


def test_errors_of_several_fields():
    assert api_errors(validation_error(Sample, {"count": -1, "status": "x"})) == {
        "count": ["Int value should be greater than 0."],
        "status": ["Value must be one of ['draft', 'active']."],
    }


def test_conversion_errors_hide_validation_ones():
    assert api_errors(validation_error(Sample, {"title": 1, "count": -1})) == {
        "title": ["Couldn't interpret '1' as string."]
    }


def test_rogue_fields_go_first():
    assert list(api_errors(validation_error(Sample, {"count": "x", "foo": 1}))) == ["foo", "count"]


def test_list_validation_errors_keep_failed_items_only():
    class Item(BaseModel):
        count: int = Field(ge=0)

    class Items(BaseModel):
        items: list[Item]

    assert api_errors(validation_error(Items, {"items": [{"count": 1}, {"count": -1}, {"count": -2}]})) == {
        "items": [
            {"count": ["Int value should be greater than 0."]},
            {"count": ["Int value should be greater than 0."]},
        ]
    }


def test_list_conversion_errors_keep_the_first_item_only():
    assert api_errors(validation_error(Sample, {"tags": [1, 2]})) == {"tags": ["Couldn't interpret '1' as string."]}


def test_error_of_object_hides_errors_of_its_fields():
    class Child(BaseModel):
        value: int | None = None

        @model_validator(mode="after")
        def check(self):
            raise ValueError("object error")

    class Parent(BaseModel):
        child: Child

    assert api_errors(validation_error(Parent, {"child": {"value": 1}})) == {"child": ["object error"]}


# --- discriminated unions ---


def test_union_tags_are_removed_from_locations():
    register_union_tags({"unionField"}, {"taxRate"})
    assert without_union_tags(("unionField", 0, "taxRate", "value")) == ("unionField", 0, "value")
    assert without_union_tags(("unionField", "taxRate", "value")) == ("unionField", "value")
    # the same name in other fields is kept
    assert without_union_tags(("other", 0, "taxRate", "value")) == ("other", 0, "taxRate", "value")


def test_discriminated_union_errors():
    class TaxRate(BaseModel):
        kind: Literal["taxRate"] = "taxRate"
        value: int = Field(ge=0)

    class ThirdParty(BaseModel):
        kind: Literal["thirdParty"] = "thirdParty"
        name: str

    class Agreement(BaseModel):
        unionChanges: list[Annotated[TaxRate | ThirdParty, Field(discriminator="kind")]]

    register_union_tags({"unionChanges"}, {"taxRate", "thirdParty"})
    assert api_errors(validation_error(Agreement, {"unionChanges": [{"kind": "taxRate", "value": -1}]})) == {
        "unionChanges": [{"value": ["Int value should be greater than 0."]}]
    }
    errors = api_errors(validation_error(Agreement, {"unionChanges": [{"kind": "x"}]}))
    assert errors == {
        "unionChanges": [
            ["Input tag 'x' found using 'kind' does not match any of the expected tags: 'taxRate', 'thirdParty'"]
        ]
    }


# --- choices of the pydantic error context ---


@pytest.mark.parametrize(
    "expected, choices",
    [
        ("'draft'", ["draft"]),
        ("'draft' or 'active'", ["draft", "active"]),
        ("'draft', 'active' or 'complete'", ["draft", "active", "complete"]),
        ("<Kind.GENERAL: 'general'> or <Kind.OTHER: 'other'>", ["general", "other"]),
        ("'black or white' or 'red'", ["black or white", "red"]),
        ("1 or 2", [1, 2]),
    ],
)
def test_expected_choices(expected, choices):
    assert expected_choices(expected) == choices


def test_expected_choices_format_of_pydantic():
    """`expected_choices` parses the `expected` context of pydantic: it must keep its format"""
    (error,) = pydantic_errors(Sample, {"status": "x"})
    assert error["ctx"]["expected"] == "'draft' or 'active'"
    (error,) = pydantic_errors(Sample, {"kind": "x"})
    assert error["ctx"]["expected"] == "'general' or 'other'"
