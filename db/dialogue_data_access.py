from typing import Optional, List
from db.database import Session
from db.database import init_db
from db.models import Dialogue
from enums import ContentType  # 如果需要的话

class DialogueDataAccess:
    def __init__(self):
        # init_db()
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_data(self, content_id: int, role: str, message: str, img_path: str = None) -> None:
        """Insert data into the Dialogue table."""
        new_data = Dialogue(
            content_id=content_id,
            role=role,
            message=message,
            img_path=img_path
        )
        try:
            self.session.add(new_data)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

    def get_data_by_id(self, data_id: int) -> Optional[Dialogue]:
        """Retrieve a record by its ID."""
        try:
            data = self.session.query(Dialogue).filter(Dialogue.id == data_id).one_or_none()
            return data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_all_data(self) -> List[Dialogue]:
        """Retrieve all records."""
        try:
            data_list = self.session.query(Dialogue).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_data_by_content_id(self, content_id: int) -> List[Dialogue]:
        """Retrieve all records associated with a specific content_id."""
        try:
            data_list = self.session.query(Dialogue).filter(Dialogue.content_id == content_id).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def update_data(self, data_id: int, role: str = None, message: str = None, img_path: str = None) -> None:
        """Update a record by its ID."""
        try:
            data = self.session.query(Dialogue).filter(Dialogue.id == data_id).one_or_none()
            if data:
                if role is not None:
                    data.role = role
                if message is not None:
                    data.message = message
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
            data = self.session.query(Dialogue).filter(Dialogue.id == data_id).one_or_none()
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
    with DialogueDataAccess() as dda:
        dda.insert_data(content_id=1, role="user", message="Hello, how are you?", img_path="path/to/image.jpg")
        all_data = dda.get_all_data()
        print(all_data)
