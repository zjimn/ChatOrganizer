from typing import Optional, List

from sqlalchemy import Column
from sqlalchemy.sql.operators import like_op

from db.database import Session
from db.database import init_db
from db.models import ContentData, Dialogue
from enums import ContentType
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

    def insert_data(self, content_type: str, describe: str, content: str, img_path: str) -> int | None:
        """Insert data into the ContentData table."""
        new_data = ContentData(
            type=content_type,
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

    def get_data_by_id(self, data_id: int) -> Optional[ContentData]:
        """Retrieve a record by its ID."""
        try:
            data = self.session.query(ContentData).filter(ContentData.id == data_id, ContentData.delete_time.is_(None)).one_or_none()
            return data
        except Exception as e:
            print(f"An error occurred: {e}")
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

    def get_data_by_describe_or_content(self, search: str, content_type) -> List[ContentData]:
        """
        Retrieve all TXT records where describe or content in Dialogue contains the search term,
        and delete_time in ContentData is None.
        """
        try:
            # Step 1: Search for Dialogue records with the search term in describe or message
            dialogue_ids = (
                self.session.query(Dialogue.content_id)
                .filter(
                    or_(
                        Dialogue.message.like(f"%{search}%"),
                        Dialogue.content_data.has(ContentData.describe.like(f"%{search}%"))
                    ),
                    Dialogue.delete_time.is_(None)  # Filter for non-null delete_time in Dialogue
                )
                .distinct()  # Ensure unique content_ids
                .subquery()  # Use as a subquery to join with ContentData
            )

            # Step 2: Query ContentData based on the content_ids retrieved from Dialogue
            data_list = (
                self.session.query(ContentData)
                .filter(
                    ContentData.type == content_type,  # Filter for TXT type records
                    ContentData.id.in_(dialogue_ids),  # Match content_ids in ContentData
                    ContentData.delete_time.is_(None)  # Filter for non-null delete_time in ContentData
                )
                .all()
            )
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_all_image_data(self) -> List[ContentData]:
        """Retrieve all records where type is IMG."""
        try:
            data_list = self.session.query(ContentData).filter(ContentData.type == ContentType.IMG.value, ContentData.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def update_data(self, data_id: int, content_type: str = None, describe: str = None, content: str = None, img_path: str = None) -> None:
        """Update a record by its ID."""
        try:
            data = self.session.query(ContentData).filter(ContentData.id == data_id, ContentData.delete_time.is_(None)).one_or_none()
            if data:
                if content_type is not None:
                    data.type = content_type
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
                data.delete_time = datetime.utcnow()

                # Set delete_time for all related Dialogue records
                for dialogue in data.dialogues:
                    dialogue.delete_time = datetime.utcnow()

                self.session.commit()
            else:
                print("No record found with the provided ID.")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

# Example usage:
if __name__ == "__main__":
    with ContentDataAccess() as cda:
        cda.insert_data("txt", "example_description", "example_content", "path/to/image.jpg")
        all_data = cda.get_all_data()
        print(all_data)