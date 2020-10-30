from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    ForeignKey,
    Table
)

Base = declarative_base()

post_tag = Table(
    'post_tag',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id'), nullable=False),
    Column('tag_id', Integer, ForeignKey('tag.id'), nullable=False),
)


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, unique=False, nullable=False)
    date = Column(DateTime, unique=False, nullable=False)
    img_url = Column(String, unique=False, nullable=True)
    writer_id = Column(Integer, ForeignKey('writer.id'), nullable=False)
    writer = relationship('Writer', back_populates='posts')
    comments = relationship('Comment')
    tags = relationship('Tag', secondary=post_tag, back_populates='posts')


class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False, nullable=False)
    posts = relationship('Post')
    comments = relationship('Comment')


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, autoincrement=True, primary_key=True)
    writer_id = Column(Integer, ForeignKey('writer.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    content = Column(String, unique=False, nullable=False)
    writer = relationship('Writer', back_populates='comments')
    post = relationship('Post', back_populates='comments')


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    posts = relationship('Post', secondary=post_tag)
