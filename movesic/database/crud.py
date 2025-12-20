# create

from functools import wraps

from sqlalchemy import select

from movesic.database import model, session


# create


async def _create_cls(cls, new_object, **kwargs):
    if new_object and kwargs:
        raise RuntimeError("You should provide only arguments or only ready object")
    if not new_object:
        new_object = cls(**kwargs)
    async with session() as ass:
        ass.add(new_object)
    return new_object


async def create_application(new_object=None, **kwargs):
    return await _create_cls(model.Application, new_object, **kwargs)


async def create_credentials(new_object=None, **kwargs):
    return await _create_cls(model.Credentials, new_object, **kwargs)


# read


def getter_wrap(func):
    @wraps(func)
    async def _get_cls(*args, **kwargs):
        query, single = await func(*args, **kwargs)
        async with session() as ass:
            results = await ass.execute(query)
            if single:
                return results.scalars().one_or_none()
            else:
                return list(results.scalars().all())

    return _get_cls


@getter_wrap
async def get_application(
    id=None,
    *,
    type: model.SERVICETYPE_ENUM | None = None,
):
    query = select(model.Application)
    if id:
        query = query.where(model.Application.id == id)
    if type:
        query = query.where(model.Application.type == type)
    return query, id


@getter_wrap
async def get_credentials(id=None):
    query = select(model.Credentials)
    if id:
        query = query.where(model.Credentials.id == id)
    return query, id


# update


async def _update_cls(cls, comp_id, value, **kwargs):
    statement = select(cls).where(comp_id == value)
    ass = session()
    async with ass as ass:
        entry = await ass.execute(statement)
        entry = entry.scalar_one_or_none()
        if entry:
            for k in kwargs:
                setattr(entry, k, kwargs[k])
            ass.add(entry)
            return entry
    return None


async def update_application(id, **kwargs):
    return await _update_cls(model.Application, model.Application.id, id, **kwargs)


async def update_credentials(id, **kwargs):
    return await _update_cls(model.Credentials, model.Credentials.id, id, **kwargs)
