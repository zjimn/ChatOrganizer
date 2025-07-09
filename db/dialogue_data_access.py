from datetime import datetime
from typing import Optional, List
from sqlalchemy import update
from db.database import Session
from db.models import Dialogue
from util.logger import logger


class DialogueDataAccess:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_data(self, content_id: int, role: str, message: str, img_path: str = None, model_name = None, model_id = None) -> None:
        new_data = Dialogue(
            content_id=content_id,
            role=role,
            message=message,
            img_path=img_path,
            model_name=model_name,
            model_id=model_id,
        )
        try:
            self.session.add(new_data)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)

    def insert_data_by_object(self, data: Dialogue) -> int | None:
        new_data = data
        try:
            self.session.add(new_data)
            self.session.commit()
            return new_data.id
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)
            return None

    def get_data_by_id(self, data_id: int) -> Optional[Dialogue]:
        try:
            data = self.session.query(Dialogue).filter(Dialogue.id == data_id,
                                                       Dialogue.delete_time.is_(None)).one_or_none()
            return data
        except Exception as e:
            logger.log('error', e)
            return None

    def get_all_data(self) -> List[Dialogue]:
        try:
            data_list = self.session.query(Dialogue).filter(Dialogue.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            logger.log('error', e)
            return []

    def get_data_by_content_id(self, content_id: int) -> List[Dialogue]:
        try:
            data_list = self.session.query(Dialogue).filter(Dialogue.content_id == content_id,
                                                            Dialogue.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            logger.log('error', e)
            return []

    def update_data(self, data_id: int, role: str = None, message: str = None, img_path: str = None) -> None:
        try:
            data = self.session.query(Dialogue).filter(Dialogue.id == data_id,
                                                       Dialogue.delete_time.is_(None)).one_or_none()
            if data:
                if role is not None:
                    data.role = role
                if message is not None:
                    data.message = message
                if img_path is not None:
                    data.img_path = img_path
                self.session.commit()
            else:
                logger.log('error', "没有匹配指定id的数据")
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)

    def batch_update_data(self, updates: list[Dialogue]) -> None:
        try:
            for dialogue in updates:
                id = dialogue.id
                if not id:
                    logger.log('warning', "Skipping update with missing data_id.")
                    continue
                stmt = (
                    update(Dialogue)
                    .where(Dialogue.id == id, Dialogue.delete_time.is_(None))
                    .values({
                        'message': dialogue.message,
                        'img_path': dialogue.img_path,
                        'delete_time': dialogue.delete_time
                    })
                )
                self.session.execute(stmt)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', f"An error occurred during batch update: {e}")

    def delete_data(self, data_id: int) -> None:
        try:
            data = self.session.query(Dialogue).filter(Dialogue.id == data_id,
                                                       Dialogue.delete_time.is_(None)).one_or_none()
            if data:
                data.delete_time = datetime.now()
                self.session.commit()
            else:
                logger.log('error', "没有匹配指定id的数据")
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)