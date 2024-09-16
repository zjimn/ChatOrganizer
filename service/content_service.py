import json
import os
from typing import Optional

from db.content_data_access import ContentDataAccess
from db.dialogue_data_access import DialogueDataAccess
from db.models import ContentData
from config.enum import ContentType

class ContentService:
    def __init__(self):
        self.content_data_access = ContentDataAccess()
        self.dialogue_data_access = DialogueDataAccess()

    def load_records(self, file_path: str):
        """Load JSON records from a file."""
        if not os.path.isfile(file_path):
            return []  # Return an empty list if the file does not exist

        # Check if the file is empty
        if os.stat(file_path).st_size == 0:
            return []  # Return an empty list if the file is empty

        # Load the JSON content from the file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def load_txt_records(self, txt="", selected_content_hierarchy_child_id=None, content_id=None):
        """Load text records based on provided filters."""
        return self.content_data_access.get_data_by_describe_or_content(txt, ContentType.TXT.value, selected_content_hierarchy_child_id, content_id=content_id)

    def load_img_records(self, txt="", selected_content_hierarchy_child_id=None, content_id=None):
        """Load image records based on provided filters."""
        return self.content_data_access.get_data_by_describe_or_content(txt, ContentType.IMG.value, selected_content_hierarchy_child_id)

    def update_data(self, content_id, type, describe, content):
        """Update content data in the database."""
        self.content_data_access.update_data(content_id, type, None, describe, content)

    def save_img_record(self, content_id, content_hierarchy_child_id, prompt, db_img_path):
        """Save image record, inserting dialogue data if needed."""
        if content_id is None:
            content_id = self.content_data_access.insert_data(ContentType.IMG.value, content_hierarchy_child_id, prompt, "", db_img_path)
        self.dialogue_data_access.insert_data(content_id, "user", prompt)
        self.dialogue_data_access.insert_data(content_id, "assistant", "", db_img_path)
        return content_id

    def save_txt_record(self, content_id, content_hierarchy_child_id, prompt, content):
        """Save text record, inserting dialogue data if needed."""
        if content_id is None:
            content_id = self.content_data_access.insert_data(ContentType.TXT.value, content_hierarchy_child_id, prompt, content, "")
        self.dialogue_data_access.insert_data(content_id, "user", prompt)
        self.dialogue_data_access.insert_data(content_id, "assistant", content)
        return content_id

    def load_data(self, content_id) -> Optional[ContentData]:
        """Load complete data including dialogues for a specific content ID."""
        content = self.load_txt_dialogs_with_merge(content_id)
        data = self.content_data_access.get_data_by_id(content_id)
        describe = data.describe
        new_data = ContentData(
            id=data.id,
            type=data.type,
            describe=describe,
            content=content,
            dialogues=data.dialogues
        )
        return new_data

    def load_txt_dialogs_with_merge(self, content_id):
        """Load text dialogues and merge them into a single string."""
        all_data = self.dialogue_data_access.get_data_by_content_id(content_id)
        return self.merge_txt_content(all_data)

    def load_txt_dialogs(self, content_id):
        """Load text dialogues without merging."""
        return self.dialogue_data_access.get_data_by_content_id(content_id)

    def load_img_dialogs(self, content_id):
        """Load image dialogues."""
        return self.dialogue_data_access.get_data_by_content_id(content_id)

    @staticmethod
    def merge_txt_content(data):
        """Merge text content from dialogue data into a single string."""
        return "\n".join(f"{item.role}: {item.message}\n" for item in data)

# Example usage
if __name__ == "__main__":
    content_service = ContentService()
    # Example calls
    records = content_service.load_txt_records(txt="example")
    content_id = content_service.save_txt_record(None, 1, "Example Prompt", "Example Content")
    data = content_service.load_data(content_id)
    print(records, content_id, data)
