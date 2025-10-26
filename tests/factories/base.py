from typing import Any, List

from factory import Factory

from prozorro_cdb.api.database.store import BaseCollection


class BaseFactory(Factory):
    class Meta:
        abstract = True

    @staticmethod
    def get_collection() -> BaseCollection:
        raise NotImplementedError()

    @classmethod
    async def db_create_batch(cls, size: int, **kwargs: Any) -> List[Any]:
        return [await cls.create(**kwargs) for _ in range(size)]

    @classmethod
    async def create(
        cls,
        **kwargs: Any,
    ) -> Any:
        model = cls.build(**kwargs)

        collection = cls.get_collection()
        await collection.collection.insert_one(model.model_dump(by_alias=True, mode="json"))

        return model
