from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base


class ContentData(Base):
    __tablename__ = 'content_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    describe = Column(Text)
    content = Column(Text)
    img_path = Column(String)
    create_time = Column(DateTime, default=datetime.now)
    delete_time = Column(DateTime, nullable=True, default=None)
    content_hierarchy_child_id = Column(Integer, nullable=True)
    dialogues = relationship('Dialogue', order_by='Dialogue.id', back_populates='content_data',
                             cascade='all, delete-orphan')


class Dialogue(Base):
    __tablename__ = 'dialogue'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer, ForeignKey('content_data.id'), nullable=False)
    role = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    img_path = Column(String)
    create_time = Column(DateTime, default=datetime.now)
    delete_time = Column(DateTime, nullable=True, default=None)
    content_data = relationship('ContentData', back_populates='dialogues')


class ContentHierarchy(Base):
    __tablename__ = 'content_hierarchy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    parent_id = Column(Integer, nullable=True)
    child_id = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False, default=0)
    preset_id = Column(Integer, nullable=True)
    create_time = Column(DateTime, default=datetime.now)
    delete_time = Column(DateTime, nullable=True, default=None)


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    create_time = Column(DateTime, default=datetime.now)
    delete_time = Column(DateTime, nullable=True, default=None)


class DialoguePreset(Base):
    __tablename__ = 'dialogue_preset'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    max_history_count = Column(Integer, nullable=True, default=0)
    create_time = Column(DateTime, default=datetime.now)
    delete_time = Column(DateTime, nullable=True, default=None)

class DialoguePresetDetail(Base):
    __tablename__ = 'dialogue_preset_detail'
    id = Column(Integer, primary_key=True, autoincrement=True)
    preset_id = Column(Integer, nullable=True)
    value = Column(String)
    create_time = Column(DateTime, default=datetime.now)
    delete_time = Column(DateTime, nullable=True, default=None)


class DialogueModel(Base):
    __tablename__ = 'dialogue_model'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    type = Column(String, nullable=False)
    create_time = Column(DateTime, default=datetime.now)
    delete_time = Column(DateTime, nullable=True, default=None)