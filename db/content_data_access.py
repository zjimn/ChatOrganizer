from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import func, select, desc, asc
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, Query
from config.enum import ContentType
from db.content_hierarchy_access import ContentHierarchyDataAccess
from db.database import Session
from db.models import ContentData, Dialogue


class ContentDataAccess:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_data(self, content_type: str, content_hierarchy_child_id: int, describe: str, content: str,
                    img_path: str) -> int | None:
        new_data = ContentData(
            type=content_type,
            content_hierarchy_child_id=content_hierarchy_child_id,
            describe=describe,
            content=content,
            img_path=img_path
        )
        try:
            self.session.add(new_data)
            self.session.commit()
            return new_data.id
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")
            return None

    def insert_data_by_object(self, data: ContentData) -> int | None:
        new_data = data
        try:
            self.session.add(new_data)
            self.session.commit()
            return new_data.id
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")
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
            print(f"An error occurred while retrieving data: {e}")
            return None

    def get_all_data(self) -> list:
        try:
            data_list = self.session.query(ContentData).filter(ContentData.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_all_txt_data(self) -> List[ContentData]:
        try:
            data_list = self.session.query(ContentData).filter(ContentData.type == ContentType.TXT.value,
                                                               ContentData.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

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
            dialogue_ids_query = (
                self.session.query(Dialogue.content_id)
                .filter(
                    Dialogue.message.like(f"%{search}%"),
                    Dialogue.delete_time.is_(None),
                    or_(
                        content_id is None,
                        Dialogue.content_id == content_id
                    )
                )
                .distinct()
            )
            dialogue_ids = dialogue_ids_query.all()
            dialogue_content_ids = [dialogue[0] for dialogue in dialogue_ids]
            base_query = (
                self.session.query(ContentData)
                .filter(
                    ContentData.type == content_type,
                    or_(
                        ContentData.describe.like(f"%{search}%"),
                        ContentData.id.in_(dialogue_content_ids),
                    ),
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
            print(f"An error occurred: {e}")
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
            print(f"An error occurred: {e}")
            return [], 0

    def get_all_image_data(self) -> List[ContentData]:
        try:
            data_list = self.session.query(ContentData).filter(ContentData.type == ContentType.IMG.value,
                                                               ContentData.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def update_data(self, data_id: int, content_type: str = None, content_hierarchy_child_id=None, describe: str = None,
                    content: str = None, img_path: str = None) -> None:
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
                self.session.commit()
            else:
                print("No record found with the provided ID.")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

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
                print("No record found with the provided ID.")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")