from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from app import db

ModelType = db.Model


@dataclass
class BaseDbService:
    """Base DB service with list, get, create, update & delete methods."""

    model: type[db.Model]
    db_session: AsyncSession

    async def list(self, **kwargs: Any) -> list[ModelType]:
        """
        The list function returns all ModelType objects in the database.

        Args:
            kwargs:: The id of the object

        Returns:
            A list of objects that are instances of the ModelType
        """

        statement = select(self.model).filter_by(**kwargs)
        result = await self.db_session.execute(statement)
        objs: list[ModelType] = result.scalars().all()
        return objs

    async def get(self, id_: UUID4) -> ModelType:
        """
        The get function is used to retrieve a single object from the database.
        It takes an id and returns the corresponding object, or raises an
        HTTP 404 error if no matching object exists.

        Args:
            id_:UUID4: The id of the object

        Returns:
            The object of ModelType that has the id param as its primary key
        """

        statement = select(self.model).where(self.model.id == id_)
        result = await self.db_session.execute(statement)
        try:
            obj: ModelType = result.scalar_one()
            return obj
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__.lower()} not found",
            )

    async def create(
        self,
        obj: CreateSchemaType,
        **kwargs,
    ) -> ModelType:
        """
        The create function makes a new object of the type specified in the
        CreateSchemaType parameter. It takes an argument of obj which is an
        instance of CreateSchemaType and returns a ModelType object.

        Args:
            obj:CreateSchemaType: Specify the schema to use for validation

        Returns:
            The created ModelType object
        """

        db_obj: ModelType = self.model(**dict(**obj.dict(), **kwargs))
        self.db_session.add(db_obj)
        await self.db_session.commit()
        return await self.get(db_obj.id)

    async def update(
        self,
        id_: UUID4,
        obj: UpdateSchemaType,
    ) -> ModelType:
        """
        The update function updates an existing object in the database.
        It takes two arguments, id_ and obj. The id_ argument is the unique
        identifier of a specific object in the database, and obj is a
        dictionary containing all the columns to be updated for that object.

        Args:
            id_:UUID4: Identify the object to update
            obj:UpdateSchemaType: Specify the schema for data validation

        Returns:
            The updated object
        """

        db_obj = await self.get(id_)
        for column, value in obj.dict(exclude_unset=True).items():
            setattr(db_obj, column, value)
        await self.db_session.commit()
        return db_obj

    async def delete(self, id_: UUID4) -> JSONResponse:
        """
        The delete function is used to delete an item from the database.
        It takes a UUID4 as an argument and deletes the object with that ID
        from the database. The function returns a JSONResponse containing a
        message confirming that it was deleted.

        Args:
            id_:UUID4: Get the id of the object that is to be deleted

        Returns:
            A JSONResponse containing a message confirming that it was deleted
        """

        db_obj = await self.get(id_)
        await self.db_session.delete(db_obj)
        await self.db_session.commit()
        item_data = {
            "status": True,
            "message": f"The {self.model.__name__.lower()} has been deleted",
        }
        return JSONResponse(content=item_data)
