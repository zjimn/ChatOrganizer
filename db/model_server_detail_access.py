from datetime import datetime
from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from db.database import Session
from db.models import ModelServerDetail
from util.logger import logger


class ModelServerDetailAccess:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def get_data_by_server_key(self, server_key: str) -> Optional[ModelServerDetail]:
        try:
            data = self.session.query(ModelServerDetail).filter(ModelServerDetail.server_key == server_key, ModelServerDetail.delete_time.is_(None)).first()
            return data
        except Exception as e:
            logger.log('error', e)
            return None

    def get_all(self) -> List[ModelServerDetail]:
        try:
            return self.session.query(ModelServerDetail).filter(ModelServerDetail.delete_time.is_(None)).all()
        except Exception as e:
            logger.log('error', e)
            return []

    def upsert(self, server_key: str, txt_model_id: str = None, img_model_id: str = None, api_key: str = None, api_url: str = None, test_model_name: str = None) -> None:
        try:
            data = self.session.query(ModelServerDetail).filter(ModelServerDetail.server_key == server_key, ModelServerDetail.delete_time.is_(None)).one_or_none()
            if not data:
                data = ModelServerDetail()
                data.server_key = server_key
                if txt_model_id is not None:
                    data.txt_model_id = txt_model_id
                if img_model_id is not None:
                    data.img_model_id = img_model_id
                if api_key is not None:
                    data.api_key = api_key
                if api_url is not None:
                    data.api_url = api_url
                if test_model_name is not None:
                    data.test_model_name = test_model_name
                self.session.add(data)
                self.session.commit()
            else:
                if txt_model_id is not None:
                    data.txt_model_id = txt_model_id
                if img_model_id is not None:
                    data.img_model_id = img_model_id
                if api_key is not None:
                    data.api_key = api_key
                if api_url is not None:
                    data.api_url = api_url
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', f"Failed to upsert data for server_key {server_key}: {e}")


    def update_txt_model(self, server_key: str, txt_model_id: str) -> None:
        try:
            data = self.session.query(ModelServerDetail).filter(ModelServerDetail.server_key == server_key, ModelServerDetail.delete_time.is_(None)).one_or_none()
            data.txt_model_id = txt_model_id
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', f"Failed to upsert data for server_key {server_key}: {e}")


    def remove_model(self, model_id: int) -> None:
        try:
            data = self.session.query(ModelServerDetail).filter(or_(ModelServerDetail.txt_model_id == model_id), ModelServerDetail.delete_time.is_(None)).all()
            for item in data:
                item.txt_model_id = None
            self.session.commit()
            data = self.session.query(ModelServerDetail).filter(or_(ModelServerDetail.img_model_id == model_id), ModelServerDetail.delete_time.is_(None)).all()
            for item in data:
                item.img_model_id = None
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', f"Failed to remove model data for model_id {model_id}: {e}")


    def update_img_model(self, server_key: str, img_model_id: str) -> None:
        try:
            data = self.session.query(ModelServerDetail).filter(ModelServerDetail.server_key == server_key, ModelServerDetail.delete_time.is_(None)).one_or_none()
            data.img_model_id = img_model_id
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', f"Failed to upsert data for server_key {server_key}: {e}")

    def delete(self, server_key: str) -> None:
        try:
            list = self.session.query(ModelServerDetail).filter(ModelServerDetail.server_key == server_key, ModelServerDetail.delete_time.is_(None)).one_or_none()
            for item in list:
                if item:
                    item.delete_time = datetime.now()
                    self.session.add(item)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)

    def has_data(self) -> bool:
        try:
            exists = self.session.query(ModelServerDetail).filter(
                ModelServerDetail.delete_time.is_(None)
            ).first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.log('error', e)
            return False