from datetime import datetime
from typing import Optional, List, Dict

from sqlalchemy import asc

from db.database import Session
from db.models import ContentHierarchy, ContentData, Dialogue


class ContentHierarchyDataAccess:
    def __init__(self):
        # Initialize the database session
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_data(self, parent_id: Optional[int], child_id: int, name: str, level: int) -> None:
        """Insert data into the ContentHierarchy table."""
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
        """Retrieve a record by its ID."""
        try:
            data = self.session.query(ContentHierarchy).filter(ContentHierarchy.id == data_id, ContentHierarchy.delete_time.is_(None)).one_or_none()
            return data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_all_data(self) -> List[ContentHierarchy]:
        """Retrieve all records."""
        try:
            data_list = self.get_all_children_by_parent_id()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_all_children_by_parent_id(self, parent_id: int = None) -> List[ContentHierarchy]:
        """Retrieve all records associated with a specific parent_id by querying all data once."""
        try:
            if parent_id is not None:
                parent_id = int(parent_id)

            # Step 1: Query all records once
            all_records = (self.session.query(ContentHierarchy)
                           .filter(ContentHierarchy.delete_time.is_(None))
                           .order_by(asc(ContentHierarchy.parent_id), asc(ContentHierarchy.child_id))
                           .all())

            # Step 2: Build a parent-child dictionary
            parent_child_map: Dict[int, List[ContentHierarchy]] = {}
            for record in all_records:
                if record.parent_id in parent_child_map:
                    parent_child_map[record.parent_id].append(record)
                else:
                    parent_child_map[record.parent_id] = [record]

            # Step 3: Recursive function to collect all children
            def collect_children(pid: int) -> List[ContentHierarchy]:
                all_children = []
                children = parent_child_map.get(pid, [])
                for child in children:
                    all_children.append(child)
                    # Recursively collect all children of this child
                    all_children.extend(collect_children(child.child_id))
                return all_children

            # Start collecting from the specified parent_id
            result = collect_children(parent_id)

            # Adding records where child.child_id == parent_id to the result
            if parent_id is not None:
                for record in all_records:
                    if record.child_id == parent_id and record not in result:
                        result.append(record)

            return result

        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def update_data(self, child_id: int, parent_id: Optional[int] = None, name: Optional[str] = None, level: Optional[int] = None) -> None:
        """Update a record by its ID."""
        try:
            data = self.session.query(ContentHierarchy).filter(ContentHierarchy.child_id == child_id, ContentHierarchy.delete_time.is_(None)).one_or_none()
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
        """Update the delete_time of a record, its child records, and associated dialogues."""
        try:
            # 递归更新所有子记录及其关联的内容
            def update_record_and_children(record_id):
                # 查找主记录
                record = self.session.query(ContentHierarchy).filter(ContentHierarchy.child_id == record_id,
                                                                     ContentHierarchy.delete_time.is_(
                                                                         None)).one_or_none()

                if record:
                    # 更新主记录的 delete_time
                    record.delete_time = datetime.now()

                    # 查找与主记录关联的 ContentData 记录
                    content_data_records = self.session.query(ContentData).filter(
                        ContentData.content_hierarchy_child_id == record.child_id).all()

                    for content_data in content_data_records:
                        # 更新 ContentData 记录的 delete_time
                        content_data.delete_time = datetime.utcnow()

                        # 查找与 ContentData 关联的 Dialogue 记录
                        dialogue_records = self.session.query(Dialogue).filter(
                            Dialogue.content_id == content_data.id).all()

                        # 更新 Dialogue 记录的 delete_time
                        for dialogue in dialogue_records:
                            dialogue.delete_time = datetime.now()

                    # 递归处理所有子记录
                    child_records = self.session.query(ContentHierarchy).filter(
                        ContentHierarchy.parent_id == record_id).all()
                    for child_record in child_records:
                        update_record_and_children(child_record.child_id)

            # 开始更新主记录及其子记录
            update_record_and_children(child_id)

            # 提交更改
            self.session.commit()

        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")