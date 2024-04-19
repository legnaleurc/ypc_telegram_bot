from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Murmur(Base):
    __tablename__ = "murmur"

    id: Mapped[int] = mapped_column(primary_key=True)
    sentence: Mapped[str] = mapped_column(nullable=False)
    note: Mapped[str] = mapped_column(nullable=False)
