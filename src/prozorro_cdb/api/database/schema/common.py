from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, HttpUrl


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class Guarantee(BaseModel):
    """Guarantee with amount and currency"""

    amount: float = Field(..., ge=0, description="Amount as a number")
    currency: str = Field(default="UAH", min_length=3, max_length=3, description="3-letter ISO 4217 currency code")


class Value(Guarantee):
    """Value extending Guarantee"""

    valueAddedTaxIncluded: bool = Field(default=True)
    denominator: Decimal | None = None
    addition: Decimal | None = None


class Unit(BaseModel):
    """Measurement unit for items"""

    name: str | None = None
    name_en: str | None = None
    name_ru: str | None = None
    value: Value | None = None
    code: str


class Classification(BaseModel):
    """Base classification model"""

    scheme: str = Field(..., description="The classification scheme for the goods")
    id: str = Field(..., description="The classification ID from the scheme used")
    description: str = Field(..., description="Description of the goods, services to be provided")
    description_en: str | None = None
    description_ru: str | None = None
    uri: HttpUrl | None = None


class AdditionalClassification(Classification):
    pass


class CPVClassification(Classification):
    scheme: Literal["CPV", "ДК021"] = Field(default="CPV")


class Period(BaseModel):
    """Time period with start and end dates"""

    startDate: datetime | None = Field(None, description="The start date for the period")
    endDate: datetime | None = Field(None, description="The end date for the period")
