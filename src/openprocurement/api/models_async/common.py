from datetime import datetime
from decimal import Decimal
from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, HttpUrl, confloat, constr


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


DataT = TypeVar("DataT")


class DataModel(BaseModel, Generic[DataT]):
    data: DataT


class Guarantee(BaseModel):
    """Guarantee with amount and currency"""

    amount: confloat(ge=0) = Field(..., description="Amount as a number")
    currency: constr(min_length=3, max_length=3) = Field(default="UAH", description="3-letter ISO 4217 currency code")


class Value(Guarantee):
    """Value extending Guarantee"""

    valueAddedTaxIncluded: bool = Field(default=True)
    denominator: Optional[Decimal] = None
    addition: Optional[Decimal] = None


class Unit(BaseModel):
    """Measurement unit for items"""

    name: Optional[str] = None
    name_en: Optional[str] = None
    name_ru: Optional[str] = None
    value: Optional[Value] = None
    code: str


class Classification(BaseModel):
    """Base classification model"""

    scheme: str = Field(..., description="The classification scheme for the goods")
    id: str = Field(..., description="The classification ID from the scheme used")
    description: str = Field(..., description="Description of the goods, services to be provided")
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    uri: Optional[HttpUrl] = None


class AdditionalClassification(Classification):
    pass


class CPVClassification(Classification):
    scheme: Literal["CPV", "ДК021"] = Field(default="CPV")


class Period(BaseModel):
    """Time period with start and end dates"""

    startDate: Optional[datetime] = Field(None, description="The start date for the period")
    endDate: Optional[datetime] = Field(None, description="The end date for the period")
