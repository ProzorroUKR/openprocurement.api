from typing import List, Optional

from prozorro_cdb.api.database.schema.common import BaseModel


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
