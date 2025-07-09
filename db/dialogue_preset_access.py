from datetime import datetime
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from db.database import Session
from db.models import DialoguePreset
from util.logger import logger


class DialoguePresetAccess:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_data(self, name: str, max_history_count: int) -> int | None:
        new_data = DialoguePreset(
            name=name,
            max_history_count=max_history_count
        )
        try:
            self.session.add(new_data)
            self.session.commit()
            return new_data.id
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)
            return None

    def insert_by_object(self, data: DialoguePreset) -> int | None:
        new_data = data
        try:
            self.session.add(new_data)
            self.session.commit()
            return new_data.id
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)
            return None

    def get_data_by_id(self, data_id: int) -> Optional[DialoguePreset]:
        try:
                data = (self.session.query(DialoguePreset)
                        .filter(DialoguePreset.id == data_id,
                                DialoguePreset.delete_time.is_(None))
                        .one_or_none())
                return data
        except SQLAlchemyError as e:
            logger.log('error', e)
            return None

    def get_all_data(self) -> list:
        try:
            data_list = self.session.query(DialoguePreset).filter(DialoguePreset.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            logger.log('error', e)


    def update_data(self, id: int, name: str, max_history_count: int) -> None:
        try:
            data = self.session.query(DialoguePreset).filter(DialoguePreset.id == id,
                                                          DialoguePreset.delete_time.is_(None)).one_or_none()
            if data:
                if name is not None:
                    data.name = name
                    data.max_history_count = max_history_count
                self.session.commit()
            else:
                logger.log('error', "没有匹配指定id的数据")
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)

    def delete(self, id: int) -> None:
        try:
            data = self.session.query(DialoguePreset).filter(DialoguePreset.id == id,
                                                          DialoguePreset.delete_time.is_(None)).one_or_none()
            if data:
                data.delete_time = datetime.now()
                self.session.commit()
            else:
                logger.log('error', "没有匹配指定id的数据")
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)

    def has_data(self) -> bool:
        try:
            exists = self.session.query(DialoguePreset).filter(
                DialoguePreset.delete_time.is_(None)
            ).first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.log('error', e)
            return False