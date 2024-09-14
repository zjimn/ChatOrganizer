# models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime


class ContentData(Base):
    __tablename__ = 'content_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    describe = Column(Text)
    content = Column(Text)
    img_path = Column(String)
    create_time = Column(DateTime, default=datetime.now)
    delete_time = Column(DateTime, nullable=True, default=None)  # Field for soft delete
    content_hierarchy_child_id = Column(Integer, nullable=True)  # Field to link to ContentHierarchy's child_id

    # Enable cascading deletes on the dialogues relationship
    dialogues = relationship('Dialogue', order_by='Dialogue.id', back_populates='content_data',
                             cascade='all, delete-orphan')


class Dialogue(Base):
    __tablename__ = 'dialogue'

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer, ForeignKey('content_data.id'), nullable=False)
    role = Column(String, nullable=False)  # e.g., 'user' or 'ai'
    message = Column(Text, nullable=False)
    img_path = Column(String)
    create_time = Column(DateTime, default=datetime.now)
    delete_time = Column(DateTime, nullable=True, default=None)  # Field for soft delete

    # Relationship to ContentData
    content_data = relationship('ContentData', back_populates='dialogues')

class ContentHierarchy(Base):
    __tablename__ = 'content_hierarchy'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    parent_id = Column(Integer, nullable=True)  # Parent content ID, can be null for root items
    child_id = Column(Integer, nullable=False)  # Child content ID
    level = Column(Integer, nullable=False, default=0)  # Level in the hierarchy
    create_time = Column(DateTime, default=datetime.now)  # 创建时间
    delete_time = Column(DateTime, nullable=True, default=None)  # Field for soft delete

class Config(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), nullable=False)  # 下拉名称
    value = Column(String(255), nullable=False)  # 下拉值
    create_time = Column(DateTime, default=datetime.now)  # 创建时间
    delete_time = Column(DateTime, nullable=True, default=None)  # Field for soft delete
