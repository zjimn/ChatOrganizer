from typing import Optional, List, Tuple, Any

from sqlalchemy import Column, Tuple, func, select, desc, asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, Query, aliased
from sqlalchemy.sql.operators import like_op

from config.enum import ContentType
from db.content_hierarchy_access import ContentHierarchyDataAccess
from db.database import Session
from db.database import init_db
from db.models import ContentData, Dialogue
from datetime import datetime
from sqlalchemy import or_


class ContentDataAccess:
    def __init__(self):
        #init_db()
        self.session = Session()
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_data(self, content_type: str, content_hierarchy_child_id : int, describe: str, content: str, img_path: str) -> int | None:
        """Insert data into the ContentData table."""
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
        """Insert data into the ContentData table."""
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
        """Retrieve a ContentData record by its ID, including associated dialogues that are not soft-deleted."""
        try:
            # Start a new transaction to ensure session consistency
            with self.session.begin():
                # Query to retrieve ContentData with associated dialogues
                data = (self.session.query(ContentData)
                        .outerjoin(ContentData.dialogues)  # Outer join to include ContentData even if there are no dialogues
                        .options(joinedload(ContentData.dialogues))  # Eagerly load dialogues
                        .filter(ContentData.id == data_id,
                                ContentData.delete_time.is_(None))  # Filter ContentData
                        .one_or_none())

                if data:
                    # Filter out deleted dialogues, if any
                    data.dialogues = [d for d in data.dialogues if d.delete_time is None]

                return data
        except SQLAlchemyError as e:
            print(f"An error occurred while retrieving data: {e}")
            return None

    def get_all_data(self) -> list:
        """Retrieve all records."""
        try:
            data_list = self.session.query(ContentData).filter(ContentData.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")


    def get_all_txt_data(self) -> List[ContentData]:
        """Retrieve all records where type is TXT."""
        try:
            data_list = self.session.query(ContentData).filter(ContentData.type == ContentType.TXT.value, ContentData.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []



    def _get_base_query(self, search: str, content_type, content_hierarchy_child_id, content_id) -> 'Query':
        """
        Build the base query to be used in both paginated and non-paginated queries.
        """
        content_hierarchy_data_access = ContentHierarchyDataAccess()



        # Step 2: Determine child IDs if provided
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
            # Step 1: Search for Dialogue records with the search term in describe or message
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
                    ContentData.id.in_(dialogue_content_ids),
                    ContentData.delete_time.is_(None),
                    or_(
                        ContentData.content_hierarchy_child_id.in_(child_ids),
                        content_hierarchy_child_id is None
                    )
                )
            )

        return base_query

    def get_data_by_describe_or_content(self, search: str, content_type, content_hierarchy_child_id=None, content_id=None, sort_by = None, sort_order="asc") -> List[ContentData]:
        """
        Retrieve all TXT records where describe or content in Dialogue contains the search term,
        and delete_time in ContentData is None.
        """
        try:
            base_query = self._get_base_query(search, content_type, content_hierarchy_child_id, content_id)
            # 动态排序
            if sort_by is not None:
                # 获取排序字段，升序或降序
                sort_column = getattr(ContentData, sort_by, None)  # 根据字段名称获取对应的列
                if sort_column:
                    if sort_order == "desc":
                        base_query = base_query.order_by(desc(sort_column))
                    else:
                        base_query = base_query.order_by(asc(sort_column))
            return base_query.all()
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_data_by_describe_or_content_by_page(self, search: str, content_type, page_number: int = 1,
                                                page_size: int = 20,
                                                content_hierarchy_child_id=None, content_id=None, sort_by = None, sort_order="asc") -> tuple[
        list[Any], int]:
        """
        Retrieve paginated TXT records with the total count.
        """
        try:
            # Get the base query
            base_query = self._get_base_query(search, content_type, content_hierarchy_child_id, content_id)
            # 动态排序
            if sort_by is not None:
                # 获取排序字段，升序或降序
                sort_column = getattr(ContentData, sort_by, None)  # 根据字段名称获取对应的列
                if sort_column:
                    if sort_order == "desc":
                        base_query = base_query.order_by(desc(sort_column))
                    else:
                        base_query = base_query.order_by(asc(sort_column))

            # Get total count from the base query subquery
            subquery = base_query.subquery()
            total_count_query = select(func.count()).select_from(subquery)
            total_count = self.session.execute(total_count_query).scalar()

            # Apply pagination
            offset = (page_number - 1) * page_size
            data_list = base_query.offset(offset).limit(page_size).all()

            return data_list, total_count
        except Exception as e:
            print(f"An error occurred: {e}")
            return [], 0


    def get_all_image_data(self) -> List[ContentData]:
        """Retrieve all records where type is IMG."""
        try:
            data_list = self.session.query(ContentData).filter(ContentData.type == ContentType.IMG.value, ContentData.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def update_data(self, data_id: int, content_type: str = None,content_hierarchy_child_id = None, describe: str = None, content: str = None, img_path: str = None) -> None:
        """Update a record by its ID."""
        try:
            data = self.session.query(ContentData).filter(ContentData.id == data_id, ContentData.delete_time.is_(None)).one_or_none()
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
        """Soft delete a record by setting delete_time to the current timestamp for ContentData and related Dialogues."""
        try:
            # Fetch the ContentData record along with its related Dialogue records
            data = self.session.query(ContentData).filter(ContentData.id == data_id, ContentData.delete_time.is_(None)).one_or_none()

            if data:
                # Set delete_time to the current time for ContentData
                data.delete_time = datetime.now()

                # Set delete_time for all related Dialogue records
                for dialogue in data.dialogues:
                    dialogue.delete_time = datetime.now()

                self.session.commit()
            else:
                print("No record found with the provided ID.")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

# Example usage:
if __name__ == "__main__":
    with ContentDataAccess() as cda:
        cda.insert_data("txt", 1,"example_description", "example_content", "path/to/image.jpg")
        all_data = cda.get_all_data()
        print(all_data)