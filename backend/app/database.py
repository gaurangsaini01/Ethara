from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings


def _normalize(url: str) -> tuple[str, dict]:
    # Managed Postgres providers (Neon, Render) issue libpq-style URLs such as
    # "postgres://...?sslmode=require&channel_binding=require". The asyncpg
    # driver uses a different scheme and rejects those query params, so this
    # rewrites the scheme and translates sslmode into an asyncpg ssl arg.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://") :]

    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query))
    connect_args: dict = {}

    sslmode = query.pop("sslmode", None)
    query.pop("channel_binding", None)
    if sslmode in {"require", "verify-ca", "verify-full", "prefer", "allow"}:
        connect_args["ssl"] = True

    clean_url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    return clean_url, connect_args


_settings = get_settings()
DATABASE_URL, _CONNECT_ARGS = _normalize(_settings.database_url)

engine = create_async_engine(DATABASE_URL, connect_args=_CONNECT_ARGS, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with SessionLocal() as session:
        yield session
