from typing import List, Optional

from openprocurement.api.models_async.common import BaseModel


class ListingResponseDataModel(BaseModel):
    id: str
    dateModified: str


class PageListingModel(BaseModel):
    offset: str
    path: str
    uri: str


class ListingResponseModel(BaseModel):
    data: List[ListingResponseDataModel]
    next_page: PageListingModel
    prev_page: Optional[PageListingModel]
