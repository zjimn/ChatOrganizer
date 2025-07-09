from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import func, select, desc, asc, and_
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, Query
from config.enum import ContentType
from db.content_hierarchy_access import ContentHierarchyDataAccess
from db.database import Session
from db.models import ContentData, Dialogue
from util.logger import logger


class ContentDataAccess:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_data(self, content_type: str, content_hierarchy_child_id: int, describe: str, content: str,
                    img_path: str, query_content:str = None) -> int | None:
        new_data = ContentData(
            type=content_type,
            content_hierarchy_child_id=content_hierarchy_child_id,
            describe=describe,
            content=content,
            img_path=img_path,
            query_content=query_content
        )
        try:
            self.session.add(new_data)
            self.session.commit()
            return new_data.id
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)
            return None

    def insert_data_by_object(self, data: ContentData) -> int | None:
        new_data = data
        try:
            self.session.add(new_data)
            self.session.commit()
            return new_data.id
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)
            return None

    def get_data_by_id(self, data_id: int) -> Optional[ContentData]:
        try:
            with self.session.begin():
                data = (self.session.query(ContentData)
                        .outerjoin(ContentData.dialogues)
                        .options(joinedload(ContentData.dialogues))
                        .filter(ContentData.id == data_id,
                                ContentData.delete_time.is_(None))
                        .one_or_none())
                if data:
                    data.dialogues = [d for d in data.dialogues if d.delete_time is None]
                return data
        except SQLAlchemyError as e:
            logger.log('error', e)
            return None

    def get_all_data(self) -> list:
        try:
            data_list = self.session.query(ContentData).filter(ContentData.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            logger.log('error', e)

    def get_all_txt_data(self) -> List[ContentData]:
        try:
            data_list = self.session.query(ContentData).filter(ContentData.type == ContentType.TXT.value,
                                                               ContentData.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            logger.log('error', e)
            return []

    def parse_expression(self, expression, model, field):
        or_parts = expression.split('||')
        query_condition = None
        or_conditions = []
        for part in or_parts:
            and_parts = part.split('&&')
            and_condition = and_(*[self.parse_and_condition(part, model, field) for part in and_parts])
            or_conditions.append(and_condition)
        query_condition = or_(*or_conditions)
        return query_condition

    def parse_and_condition(self, part, model, field):
        parts = part.split('&&')
        and_conditions = [part.strip() for part in parts]
        query_condition = and_(*[self.parse_single_condition(value, model, field) for value in and_conditions])
        return query_condition

    def parse_single_condition(self, value, model, field):
        field = field.strip()
        value = value.strip().strip("'")  # 去除可能的引号
        return getattr(model, field).like(f"%{value}%")

    def _get_base_query(self, search: str, content_type, content_hierarchy_child_id, content_id) -> 'Query':
        content_hierarchy_data_access = ContentHierarchyDataAccess()
        child_ids = set()
        if content_hierarchy_child_id is not None:
            all_children = content_hierarchy_data_access.get_all_children_by_parent_id(content_hierarchy_child_id)
            child_ids = {child.child_id for child in all_children}
        if not search or search == "":
            base_query = (
                self.session.query(ContentData)
                .filter(
                    ContentData.type == content_type,
                    ContentData.delete_time.is_(None),
                    or_(
                        ContentData.content_hierarchy_child_id.in_(child_ids),
                        content_hierarchy_child_id is None
                    ),
                    or_(
                        content_id is None,
                        ContentData.id == content_id
                    )
                )
            )
        else:
            content_addition_condition = self.parse_expression(search, ContentData, "query_content")
            base_query = (
                self.session.query(ContentData)
                .filter(
                    ContentData.type == content_type,
                    content_addition_condition,
                    ContentData.delete_time.is_(None),
                    or_(
                        ContentData.content_hierarchy_child_id.in_(child_ids),
                        content_hierarchy_child_id is None
                    )
                )
            )
        return base_query

    def get_data_by_describe_or_content(self, search: str, content_type, content_hierarchy_child_id=None,
                                        content_id=None, sort_by=None, sort_order="asc") -> List[ContentData]:
        try:
            base_query = self._get_base_query(search, content_type, content_hierarchy_child_id, content_id)
            if sort_by is not None:
                sort_column = getattr(ContentData, sort_by, None)
                if sort_column:
                    if sort_order == "desc":
                        base_query = base_query.order_by(desc(sort_column))
                    else:
                        base_query = base_query.order_by(asc(sort_column))
            data_list = base_query.all()
            for item in data_list:
                self.session.expunge(item)
            return data_list
        except Exception as e:
            logger.log('error', e)
            return []

    def get_data_by_describe_or_content_by_page(self, search: str, content_type, page_number: int = 1,
                                                page_size: int = 20,
                                                content_hierarchy_child_id=None, content_id=None, sort_by=None,
                                                sort_order="asc") -> tuple[
        list[Any], int]:
        try:
            base_query = self._get_base_query(search, content_type, content_hierarchy_child_id, content_id)
            if sort_by is not None:
                sort_column = getattr(ContentData, sort_by, None)
                if sort_column:
                    if sort_order == "desc":
                        base_query = base_query.order_by(desc(sort_column))
                    else:
                        base_query = base_query.order_by(asc(sort_column))
            subquery = base_query.subquery()
            total_count_query = select(func.count()).select_from(subquery)
            total_count = self.session.execute(total_count_query).scalar()
            offset = (page_number - 1) * page_size
            data_list = base_query.offset(offset).limit(page_size).all()
            for item in data_list:
                self.session.expunge(item)
            return data_list, total_count
        except Exception as e:
            logger.log('error', e)
            return [], 0

    def get_all_image_data(self) -> List[ContentData]:
        try:
            data_list = self.session.query(ContentData).filter(ContentData.type == ContentType.IMG.value,
                                                               ContentData.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            logger.log('error', e)
            return []

    def update_data(self, data_id: int, content_type: str = None, content_hierarchy_child_id=None, describe: str = None,
                    content: str = None, img_path: str = None, query_content: str = None) -> None:
        try:
            data = self.session.query(ContentData).filter(ContentData.id == data_id,
                                                          ContentData.delete_time.is_(None)).one_or_none()
            if data:
                if content_type is not None:
                    data.type = content_type
                if content_hierarchy_child_id is not None:
                    data.content_hierarchy_child_id = content_hierarchy_child_id
                if describe is not None:
                    data.describe = describe
                if content is not None:
                    data.content = content
                if img_path is not None:
                    data.img_path = img_path
                if query_content is not None:
                    data.query_content = query_content
                self.session.commit()
            else:
                logger.log('error', "没有匹配指定id的数据")
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)

    def delete_data(self, data_id: int) -> None:
        try:
            data = self.session.query(ContentData).filter(ContentData.id == data_id,
                                                          ContentData.delete_time.is_(None)).one_or_none()
            if data:
                data.delete_time = datetime.now()
                for dialogue in data.dialogues:
                    dialogue.delete_time = datetime.now()
                self.session.commit()
            else:
                logger.log('error', "没有匹配指定id的数据")
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)