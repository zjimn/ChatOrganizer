# models.py

from sqlalchemy import Column, Integer, String, Text, DateTime
from db.database import Base
from datetime import datetime


class ContentData(Base):
    __tablename__ = 'content_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    describe = Column(Text)
    content = Column(Text)
    img_path = Column(String)
    create_time = Column(DateTime, default=datetime.utcnow)


class OperationConfig(Base):
    __tablename__ = 'operation_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), nullable=False)  # 下拉名称
    value = Column(String(255), nullable=False)  # 下拉值
    create_time = Column(DateTime, default=datetime.utcnow)  # 创建时间