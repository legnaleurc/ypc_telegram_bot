from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from tornado import options

from . import settings


Base = declarative_base()
engine = None
_Session = None


class Murmur(Base):

    __tablename__ = 'murmur'

    id = Column(Integer, primary_key=True)
    sentence = Column(String(65536), nullable=False)
    story = relationship("MurmurStory", cascade="save-update, delete")


class Meme(Base):

    __tablename__ = 'meme'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    url = Column(String(65536), nullable=False)


class MurmurStory(Base):

    __tablename__ = 'murmur_story'

    id = Column(Integer, primary_key=True)
    murmur_id = Column(Integer, ForeignKey('murmur.id', 
                                            onupdate='CASCADE',
                                            ondelete='CASCADE'),
                                            nullable=False)
    sentence = Column(String(65536), nullable=False)


@contextmanager
def Session():
    session = _Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def prepare(dsn):
    global engine
    engine = create_engine(dsn)

    # enable sqlite foreign key feature
    if engine.name.lower() == 'sqlite':
        try:
            connection = engine.raw_connection()
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.close()
        except Exception:
            print('something GG')

    Base.metadata.create_all(engine)
    global _Session
    _Session = sessionmaker(bind=engine)
