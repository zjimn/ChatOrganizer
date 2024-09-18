import json
import os
from typing import Optional

from config.constant import ASSISTANT_NAME, USER_NAME
from db.content_data_access import ContentDataAccess
from db.dialogue_data_access import DialogueDataAccess
from db.models import ContentData
from config.enum import ContentType
from util.str_util import get_chars_by_count


class ContentService:
    def __init__(self):
        pass

    def load_txt_records_by_page(self, txt = "",  tree_id = None, page_number = 1, page_size = 20, content_id = None):
        """Load text records based on provided filters."""
        with ContentDataAccess() as cda:
            return cda.get_data_by_describe_or_content_by_page(txt, ContentType.TXT.value, page_number, page_size, tree_id, content_id)

    def load_img_records_by_page(self,  txt = "",  tree_id = None, page_number = 1, page_size = 20, content_id = None):
        """Load image records based on provided filters."""
        with ContentDataAccess() as cda:
            return cda.get_data_by_describe_or_content_by_page(txt, ContentType.IMG.value, page_number, page_size, tree_id, content_id)

    def load_txt_records(self, txt = "",  tree_id = None, content_id = None):
        """Load text records based on provided filters."""
        with ContentDataAccess() as cda:
            return cda.get_data_by_describe_or_content(txt, ContentType.TXT.value, tree_id, content_id)

    def load_img_records(self,  txt = "",  tree_id = None, content_id = None):
        """Load image records based on provided filters."""
        with ContentDataAccess() as cda:
            return cda.get_data_by_describe_or_content(txt, ContentType.IMG.value, tree_id, content_id)

    def update_data(self, content_id, type, describe, content, img_path = None, dialogues = None):
        """Update content data in the database."""
        if dialogues:
            content = self.merge_txt_content(dialogues, 50)
        with ContentDataAccess() as cda:
            cda.update_data(content_id, type, None, describe, content, img_path)

    def batch_update_dialogue_data(self, data):
        """Update content data in the database."""
        with DialogueDataAccess() as dda:
            dda.batch_update_data(data)

    def save_img_record(self, content_id, tree_id, prompt, db_img_path):
        """Save image record, inserting dialogue data if needed."""
        with ContentDataAccess() as cda:
            if content_id is None:
                content_id = cda.insert_data(ContentType.IMG.value, tree_id, prompt, "",
                                                                  db_img_path)
            with DialogueDataAccess() as dda:
                dda.insert_data(content_id, "user", prompt)
                dda.insert_data(content_id, "assistant", "", db_img_path)
        return content_id

    def save_txt_record(self, content_id, tree_id, prompt, content):
        """Save text record, inserting dialogue data if needed."""
        with ContentDataAccess() as cda:
            if content_id is None:
                content_id = cda.insert_data(ContentType.TXT.value, tree_id, prompt, content, "")
            with DialogueDataAccess() as dda:
                dda.insert_data(content_id, "user", prompt)
                dda.insert_data(content_id, "assistant", content)
        return content_id

    def load_data(self, content_id: int) -> Optional[ContentData]:
        """Load complete data including dialogues for a specific content ID."""

        # Load additional data, if needed

        # Fetch data from the database
        with ContentDataAccess() as cda:
            data = cda.get_data_by_id(content_id)

            if data is None:
                print(f"No data found for content_id: {content_id}")
                return None

            # Merge content data with additional data
            content = self.merge_txt_content(data.dialogues, 50)
            # Create a new ContentData object or return the fetched data
            new_data = ContentData(
                id=data.id,
                type=data.type,
                describe=data.describe,
                content=content,
                dialogues=data.dialogues
            )

        return new_data

    def load_txt_dialogs_with_merge(self, content_id):
        """Load text dialogues and merge them into a single string."""
        with DialogueDataAccess() as dda:
            all_data = dda.get_data_by_content_id(content_id)
        return self.merge_txt_content(all_data)

    def load_txt_dialogs(self, content_id):
        """Load text dialogues without merging."""
        with DialogueDataAccess() as dda:
            return dda.get_data_by_content_id(content_id)

    def load_img_dialogs(self, content_id):
        """Load image dialogues."""
        with DialogueDataAccess() as dda:
            return dda.get_data_by_content_id(content_id)

    def merge_txt_content(self, data, max_chars = None):
        """
        Merge text content from dialogue data into a single string, limiting to a specified number of non-whitespace characters.

        :param data: List of dialogue data with 'role' and 'message'.
        :param max_chars: Maximum number of non-whitespace characters to include.
        :return: Merged string.
        """
        result = []
        char_count = 0

        for item in data:
            if item.role == USER_NAME:
                continue
            line = item.message
            result.append("\n")
            for char in line:
                if char.isspace():
                    result.append(char)  # Add space or newline, but don't count them
                else:
                    if max_chars is not None and char_count >= max_chars:
                        return ''.join(result)
                    result.append(char)
                    char_count += 1

        return get_chars_by_count(''.join(result), max_chars)


# Example usage
if __name__ == "__main__":
    content_service = ContentService()
    # Example calls
    records = content_service.load_txt_records(txt="example")
    content_id = content_service.save_txt_record(None, 1, "Example Prompt", "Example Content")
    data = content_service.load_data(content_id)
    print(records, content_id, data)
