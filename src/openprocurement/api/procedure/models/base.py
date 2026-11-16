"""
Base class for pydantic models of the API.

What the base class does on top of pydantic:

* errors have the structure and the messages of the API (see `api_errors`)
* `None` passed for a field means "not passed" (the default is applied, required fields complain)
* computed fields are accepted in the input and ignored
* `serialize()` skips `None`, empty lists and empty nested models
* errors of cross field validations can be attached to a field (see `FieldError`)
"""

import functools
from typing import Annotated, Any, Callable, ClassVar, get_args, get_origin

from pydantic import (
    AliasChoices,
    ConfigDict,
    Discriminator,
    Field,
    Tag,
    model_serializer,
    model_validator,
)
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ValidationError as PydanticValidationError
from pydantic.fields import FieldInfo

from openprocurement.api.procedure.errors import (
    DataValidationError,
    ValidationError,
    api_errors,
    field_error,
    register_union_tags,
)
from openprocurement.api.procedure.types import MD5


def model_field_validator(field: str) -> Callable[[Callable[[Any, Any], None]], Any]:
    """
    A validation of a field that needs the other fields of the model: it runs after the whole model is validated
    (`model_validator(mode="after")`), gets the model and the value of the field, its errors are attached
    to the field (see `field_error`):

        @model_field_validator("id")
        def validate_id(self, value):
            if self.scheme == KATOTTG_SCHEME and value not in KATOTTG:
                raise ValueError(f"{KATOTTG_SCHEME} id not found in standards")
    """

    def decorator(method: Callable[[Any, Any], None]) -> Any:
        @functools.wraps(method)
        def validate(self):
            with field_error(field):
                method(self, getattr(self, field))
            return self

        # the name of the method is kept (a subclass overrides the validation by it), but not its signature:
        # pydantic would take `value` for `info` of `(self, info)` after validators
        del validate.__wrapped__
        return model_validator(mode="after")(validate)

    return decorator


def union_tags_of(annotation: Any) -> set[str]:
    """
    The tags of the discriminated unions in a field type:
    `Annotated[A | B, Field(discriminator="type")]` (the `Literal` values of `type` in A and B)
    or `Annotated[Annotated[A, Tag("a")] | Annotated[B, Tag("b")], Discriminator(function)]`
    """
    tags = set()
    if get_origin(annotation) is Annotated:
        annotation, *metadata = get_args(annotation)
        for meta in metadata:
            if isinstance(meta, Tag):
                tags.add(meta.tag)
            discriminator = meta.discriminator if isinstance(meta, (FieldInfo, Discriminator)) else None
            if isinstance(discriminator, str):
                for model_class in get_args(annotation):
                    tags.update(get_args(model_class.model_fields[discriminator].annotation))
    for arg in get_args(annotation):
        tags |= union_tags_of(arg)
    return tags


class Model(PydanticBaseModel):
    model_config = ConfigDict(
        extra="forbid",  # "Rogue field"
        use_enum_values=True,  # the values of enum fields are plain strings
        regex_engine="python-re",  # `pattern` is matched from the start of the string (`re.match`)
        coerce_numbers_to_str=True,  # a string field accepts numbers
    )

    _input_names: ClassVar[frozenset[str]] = frozenset()
    _computed_names: ClassVar[frozenset[str]] = frozenset()
    _any_names: ClassVar[frozenset[str]] = frozenset()

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        input_names = set()
        any_names = set()
        for name, field in cls.model_fields.items():
            alias = field.validation_alias or field.alias
            if isinstance(alias, AliasChoices):
                names = {choice for choice in alias.choices if isinstance(choice, str)}
            else:
                names = {alias if isinstance(alias, str) else name}
            input_names.update(names)
            if tags := union_tags_of(field.annotation):
                register_union_tags({*names, field.serialization_alias or field.alias or name}, tags)
            if field.annotation is Any:
                any_names.update({name, field.serialization_alias or field.alias or name})
        cls._any_names = frozenset(any_names)
        cls._input_names = frozenset(input_names)
        # the input of a computed field is ignored by its attribute name only (not by its serialized name)
        cls._computed_names = frozenset(cls.model_computed_fields)

    @model_validator(mode="before")
    @classmethod
    def _prepare_input(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        result = {}
        for key, value in data.items():
            if key in cls._computed_names and key not in cls._input_names:
                continue  # the output of a computed field passed back
            if key in cls._input_names and value is None:
                continue  # `null` is "not passed"
            result[key] = value
        return result

    @model_serializer(mode="wrap")
    def _skip_empty(self, handler):
        data = handler(self)
        result = {}
        for key, value in data.items():
            if value is None:
                continue
            if isinstance(value, (list, dict)) and not value and key not in self._any_names:
                continue
            result[key] = value
        return result

    @classmethod
    def validate_data(cls, data: Any) -> dict:
        """
        Validates the data and returns its serialized representation.
        :raises DataValidationError: with the errors in the API format (see `api_errors`)
        """
        try:
            instance = cls.model_validate(data)
        except PydanticValidationError as e:
            raise DataValidationError(api_errors(e)) from None
        return instance.serialize()

    def serialize(self) -> dict:
        return self.model_dump(by_alias=True)


class DocumentIdMixin(Model):
    """`_id` of a database document, `id` is taken as well: `_id` when both are given"""

    id: MD5 | None = Field(None, alias="_id", validation_alias=AliasChoices("_id", "id"))  # type: ignore[pydantic-alias]

    @model_validator(mode="before")
    @classmethod
    def _one_id(cls, data: Any) -> Any:
        if isinstance(data, dict) and "_id" in data and "id" in data:
            data = {key: value for key, value in data.items() if key != "id"}  # not a rogue field
        return data


class RootModel(DocumentIdMixin):
    """A model of a database document: `_id` (see `DocumentIdMixin`), `_rev` and the service fields"""

    rev: str | None = Field(None, alias="_rev")
    doc_type: str | None = None
    public_modified: Any = None
    public_ts: Any = None
    revisions: Any = None


def validate_list_uniq_factory(*item_attrs, **_kwargs) -> Callable:
    """
    Factory for ListType validators that require unique items
    Args:
        item_attrs: item attributes for compiling unique identifier
    """
    # get custom error message
    err_msg = _kwargs.get("err_msg", "Items should be unique")
    if item_attrs:
        err_msg = f"{err_msg} by fields: {', '.join(item_attrs)}"

    # if err_field provided set custom error destination
    if err_field := _kwargs.get("err_field"):
        err_msg = [{err_field: err_msg}]

    def _get_attr(item, field_attr):
        """
        Function gets nested attribute of the provided item
        Args:
            item: item from the iterable
            field_attr: field attr, can be nested separated by '.'
        """
        for x in field_attr.split("."):
            item = getattr(item, x, None)
        return item

    def _validate_uniq(values, *args, **kwargs):
        """
        Main validator function
        Args:
            values: values for validation, iterable
            args:
            kwargs:
        """
        if values:
            res = values
            if item_attrs:
                res = [tuple(_get_attr(x, a) for a in item_attrs) for x in res]
            if len(res) > len(set(res)):
                raise ValidationError(err_msg)

    return _validate_uniq


validate_uniq = validate_list_uniq_factory()


validate_uniq_id = validate_list_uniq_factory("id")


validate_uniq_code = validate_list_uniq_factory("code")


validate_uniq_value = validate_list_uniq_factory("value")


def validate_object_id_uniq(objs):
    """the ids of the objects (models) of a list are unique"""
    if objs:
        obj_name = type(objs[0]).__name__
        obj_name_multiple = obj_name[0].lower() + obj_name[1:]
        ids = [obj.id for obj in objs]
        if ids and len(set(ids)) != len(ids):
            raise ValidationError("{} id should be uniq for all {}s".format(obj_name, obj_name_multiple))
