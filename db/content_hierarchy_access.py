from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError

from db.database import Session
from db.models import ContentHierarchy, ContentData, Dialogue


class ContentHierarchyDataAccess:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_data(self, parent_id: Optional[int], child_id: int, name: str, level: int) -> None:
        new_data = ContentHierarchy(
            parent_id=parent_id,
            child_id=child_id,
            name=name,
            level=level
        )
        try:
            self.session.add(new_data)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

    def get_data_by_id(self, data_id: int) -> Optional[ContentHierarchy]:
        try:
            data = self.session.query(ContentHierarchy).filter(ContentHierarchy.id == data_id,
                                                               ContentHierarchy.delete_time.is_(None)).one_or_none()
            return data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_all_data(self) -> List[ContentHierarchy]:
        try:
            data_list = self.get_all_children_by_parent_id()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def has_data(self) -> bool:
        try:
            exists = self.session.query(ContentHierarchy).filter(
                ContentHierarchy.delete_time.is_(None)
            ).first() is not None
            return exists
        except SQLAlchemyError as e:
            print(f"检查数据存在性时发生错误: {e}")
            return False

    def get_all_children_by_parent_id(self, parent_id: int = None) -> List[ContentHierarchy]:
        try:
            if parent_id is not None:
                parent_id = int(parent_id)
            all_records = (self.session.query(ContentHierarchy)
                           .filter(ContentHierarchy.delete_time.is_(None))
                           .order_by(asc(ContentHierarchy.parent_id), asc(ContentHierarchy.child_id))
                           .all())
            parent_child_map: Dict[int, List[ContentHierarchy]] = {}
            for record in all_records:
                if record.parent_id in parent_child_map:
                    parent_child_map[record.parent_id].append(record)
                else:
                    parent_child_map[record.parent_id] = [record]

            def collect_children(pid: int) -> List[ContentHierarchy]:
                all_children = []
                children = parent_child_map.get(pid, [])
                for child in children:
                    all_children.append(child)
                    all_children.extend(collect_children(child.child_id))
                return all_children

            result = collect_children(parent_id)
            if parent_id is not None:
                for record in all_records:
                    if record.child_id == parent_id and record not in result:
                        result.append(record)
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def update_data(self, child_id: int, parent_id: Optional[int] = None, name: Optional[str] = None,
                    level: Optional[int] = None) -> None:
        try:
            data = self.session.query(ContentHierarchy).filter(ContentHierarchy.child_id == child_id,
                                                               ContentHierarchy.delete_time.is_(None)).one_or_none()
            if data:
                if parent_id is not None:
                    data.parent_id = parent_id
                if name is not None:
                    data.name = name
                if level is not None:
                    data.level = level
                self.session.commit()
            else:
                print("No record found with the provided ID.")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

    def delete_data(self, child_id: int) -> None:
        try:
            def update_record_and_children(record_id):
                record = self.session.query(ContentHierarchy).filter(ContentHierarchy.child_id == record_id,
                                                                     ContentHierarchy.delete_time.is_(
                                                                         None)).one_or_none()
                if record:
                    record.delete_time = datetime.now()
                    content_data_records = self.session.query(ContentData).filter(
                        ContentData.content_hierarchy_child_id == record.child_id).all()
                    for content_data in content_data_records:
                        content_data.delete_time = datetime.now()
                        dialogue_records = self.session.query(Dialogue).filter(
                            Dialogue.content_id == content_data.id).all()
                        for dialogue in dialogue_records:
                            dialogue.delete_time = datetime.now()
                    child_records = self.session.query(ContentHierarchy).filter(
                        ContentHierarchy.parent_id == record_id).all()
                    for child_record in child_records:
                        update_record_and_children(child_record.child_id)

            update_record_and_children(child_id)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")
