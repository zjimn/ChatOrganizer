from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import func, select, desc, asc
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, Query
from config.enum import ContentType
from db.content_hierarchy_access import ContentHierarchyDataAccess
from db.database import Session
from db.models import DialoguePresetDetail, Dialogue
from util.logger import logger


class DialoguePresetDetailAccess:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_data(self, preset_id, value: str) -> int | None:
        new_data = DialoguePresetDetail(
            preset_id=preset_id,
            value=value,
        )
        try:
            self.session.add(new_data)
            self.session.commit()
            return new_data.id
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)
            return None

    def insert_by_object(self, data: DialoguePresetDetail) -> int | None:
        new_data = data
        try:
            self.session.add(new_data)
            self.session.commit()
            return new_data.id
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)
            return None

    def get_data_by_id(self, data_id: int) -> Optional[DialoguePresetDetail]:
        try:
                data = (self.session.query(DialoguePresetDetail)
                        .filter(DialoguePresetDetail.id == data_id,
                                DialoguePresetDetail.delete_time.is_(None))
                        .one_or_none())
                return data
        except SQLAlchemyError as e:
            logger.log('error', e)
            return None

    def get_data_by_preset_id(self, data_id: int) -> list :
        try:
                data = (self.session.query(DialoguePresetDetail)
                        .filter(DialoguePresetDetail.preset_id == data_id,
                                DialoguePresetDetail.delete_time.is_(None))
                        .all())
                return data
        except SQLAlchemyError as e:
            logger.log('error', e)
            return []

    def get_all_data(self) -> list:
        try:
            data_list = self.session.query(DialoguePresetDetail).filter(DialoguePresetDetail.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            logger.log('error', e)


    def update_data(self, id: int, value: str, delete_time) -> None:
        try:
            data = self.session.query(DialoguePresetDetail).filter(DialoguePresetDetail.id == id,
                                                          DialoguePresetDetail.delete_time.is_(None)).one_or_none()
            if data:
                if value is not None:
                    data.value = value
                if delete_time is not None:
                    data.delete_time = delete_time
                self.session.commit()
            else:
                logger.log('error', "没有匹配指定id的数据")
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)

    def delete(self, id: int) -> None:
        try:
            data = self.session.query(DialoguePresetDetail).filter(DialoguePresetDetail.id == id,
                                                          DialoguePresetDetail.delete_time.is_(None)).one_or_none()
            if data:
                data.delete_time = datetime.now()
                self.session.commit()
            else:
                logger.log('error', "没有匹配指定id的数据")
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)

    def delete_by_preset_id(self, preset_id: int) -> None:
        try:
            data = self.session.query(DialoguePresetDetail).filter(DialoguePresetDetail.preset_id == preset_id,
                                                          DialoguePresetDetail.delete_time.is_(None)).all()
            for item in data:
                if item:
                    item.delete_time = datetime.now()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)