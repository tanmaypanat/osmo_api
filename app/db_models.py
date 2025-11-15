import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

# setup postgresdb with alchemy
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class Formula(Base):
    __tablename__ = "formulas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # used for deduplication
    materials_hash = Column(String, nullable=False, unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # runtime materials list generation
    materials = relationship(
        "FormulaMaterial",
        back_populates="formula",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class FormulaMaterial(Base):
    __tablename__ = "formula_materials"

    id = Column(Integer, primary_key=True, index=True)

    formula_id = Column(
        Integer, ForeignKey("formulas.id", ondelete="CASCADE"), nullable=False
    )

    name = Column(String, nullable=False)
    concentration = Column(Float, nullable=False)

    # runtime backpopulates to formula
    formula = relationship("Formula", back_populates="materials")


def get_async_session() -> AsyncSession:
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created")


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("All tables dropped")
