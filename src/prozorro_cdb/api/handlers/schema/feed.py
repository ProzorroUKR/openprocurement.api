from prozorro_cdb.api.database.schema.common import BaseModel


class ListingResponseDataModel(BaseModel):
    id: str
    dateModified: str


class PageListingModel(BaseModel):
    offset: str
    path: str
    uri: str


class ListingResponseModel(BaseModel):
    data: list[ListingResponseDataModel]
    next_page: PageListingModel
    prev_page: PageListingModel | None
