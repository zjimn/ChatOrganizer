from typing import Optional, List
from db.database import Session
from db.database import init_db
from db.models import ContentData
from enums import ContentType


class ContentDataAccess:
    def __init__(self):
        #init_db()
        self.session = Session()
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_data(self, content_type: str, describe: str, content: str, img_path: str) -> None:
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
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

    def get_data_by_id(self, data_id: int) -> Optional[ContentData]:
        """Retrieve a record by its ID."""
        try:
            data = self.session.query(ContentData).filter(ContentData.id == data_id).one_or_none()
            return data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_all_data(self) -> list:
        """Retrieve all records."""
        try:
            data_list = self.session.query(ContentData).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")


    def get_all_txt_data(self) -> List[ContentData]:
        """Retrieve all records where type is TXT."""
        try:
            data_list = self.session.query(ContentData).filter(ContentData.type == ContentType.TXT.value).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_all_image_data(self) -> List[ContentData]:
        """Retrieve all records where type is IMG."""
        try:
            data_list = self.session.query(ContentData).filter(ContentData.type == ContentType.IMG.value).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def update_data(self, data_id: int, content_type: str = None, describe: str = None, content: str = None, img_path: str = None) -> None:
        """Update a record by its ID."""
        try:
            data = self.session.query(ContentData).filter(ContentData.id == data_id).one_or_none()
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
        """Delete a record by its ID."""
        try:
            data = self.session.query(ContentData).filter(ContentData.id == data_id).one_or_none()
            if data:
                self.session.delete(data)
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