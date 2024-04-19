from collections.abc import Sequence

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select, insert, delete, update


from ._models import Base, Murmur


class Database:
    def __init__(self, dsn: str):
        self._engine = create_engine(dsn)

    def get_murmur_list(self) -> Sequence[Murmur]:
        with Session(self._engine) as session:
            query = select(Murmur)
            rows = session.execute(query)
            return rows.scalars().all()

    def get_murmur(self, id: int) -> Murmur:
        with Session(self._engine) as session:
            query = select(Murmur).filter_by(id=id)
            rows = session.execute(query)
            rv = rows.scalar()
            if rv is None:
                raise RuntimeError(f"${id} not found")
            return rv

    def add_murmur(self, sentence: str) -> int:
        with Session(self._engine) as session:
            query = (
                insert(Murmur).values(sentence=sentence, note="").returning(Murmur.id)
            )
            rows = session.execute(query)
            id_ = rows.scalar()
            if id_ is None:
                raise RuntimeError(f"add ${sentence} failed")
            return id_

    def remove_murmur(self, id: int) -> int:
        with Session(self._engine) as session:
            query = delete(Murmur).filter_by(id=id)
            rows = session.execute(query)
            return rows.rowcount

    def set_note(self, id: int, note: str) -> None:
        with Session(self._engine) as session:
            query = update(Murmur).filter_by(id=id).values(note=note)
            session.execute(query)


def initialize(dsn: str):
    engine = create_engine(dsn)
    Base.metadata.create_all(engine)
