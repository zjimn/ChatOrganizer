from datetime import datetime
from typing import Optional, List

from sqlalchemy import update

from db.database import Session
from db.database import init_db
from db.models import Dialogue

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
            data = self.session.query(Dialogue).filter(Dialogue.id == data_id, Dialogue.delete_time.is_(None)).one_or_none()
            return data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_all_data(self) -> List[Dialogue]:
        """Retrieve all records."""
        try:
            data_list = self.session.query(Dialogue).filter(Dialogue.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_data_by_content_id(self, content_id: int) -> List[Dialogue]:
        """Retrieve all records associated with a specific content_id."""
        try:
            data_list = self.session.query(Dialogue).filter(Dialogue.content_id == content_id, Dialogue.delete_time.is_(None)).all()
            return data_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def update_data(self, data_id: int, role: str = None, message: str = None, img_path: str = None) -> None:
        """Update a record by its ID."""
        try:
            data = self.session.query(Dialogue).filter(Dialogue.id == data_id, Dialogue.delete_time.is_(None)).one_or_none()
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

    def batch_update_data(self, updates: list[Dialogue]) -> None:
        """
        Batch update multiple records by their IDs.

        Each dictionary in the updates list should contain the following keys:
        - 'data_id' (required): the ID of the record to update
        - Optional fields: 'role', 'message', 'img_path'
        """
        try:
            # Prepare update statements for each record
            for dialogue  in updates:
                id = dialogue .id
                if not id:
                    print("Skipping update with missing data_id.")
                    continue

                # Prepare the update statement
                stmt = (
                    update(Dialogue)
                    .where(Dialogue.id == id, Dialogue.delete_time.is_(None))
                    .values({
                        'message': dialogue.message,
                        'img_path': dialogue.img_path,
                        'delete_time': dialogue.delete_time
                    })
                )

                # Execute the update
                self.session.execute(stmt)

            # Commit all updates at once
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred during batch update: {e}")

    def delete_data(self, data_id: int) -> None:
        """Delete a record by its ID."""
        try:
            data = self.session.query(Dialogue).filter(Dialogue.id == data_id, Dialogue.delete_time.is_(None)).one_or_none()
            if data:
                data.delete_time = datetime.now()
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
