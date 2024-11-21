from config.constant import PREFERENCE_PROPERTIES_FILE
from util.preference_reader import PreferenceReader


class TokenManager:
    def __init__(self):
        reader = PreferenceReader(PREFERENCE_PROPERTIES_FILE)
        token_limit = reader.get("TOKEN_LIMIT", 0)
        history_limit = reader.get("HISTORY_LIMIT", 0)
        self.default_token_limit = token_limit
        self.token_limit = token_limit
        self.default_history_limit = history_limit
        self.history_limit = history_limit
        self.conversation_txt_history = []
        self.conversation_img_history = []

    def estimate_token_count(self, text):
        return len(text) // 4

    def manage_txt_history(self):
        total_tokens = sum(self.estimate_token_count(message['content']) for message in self.conversation_txt_history)
        while total_tokens > self.token_limit != 0:
            if self.conversation_txt_history:
                removed_message = self.conversation_txt_history.pop(0)
                total_tokens -= self.estimate_token_count(removed_message['content'])
            else:
                break
        while self.history_limit != 0 and len(self.conversation_txt_history) > self.history_limit:
            self.conversation_txt_history.pop(0)

    def set_history_limit(self, count):
        self.history_limit = count

    def remove_a_pair_history(self):
        if len(self.get_manage_txt_history()) > 1:
            self.conversation_txt_history.pop()
            self.conversation_txt_history.pop()

    def reset_history_limit(self):
        self.history_limit = self.default_history_limit

    def set_token_limit(self, count):
        self.token_limit = count

    def reset_token_limit(self):
        self.token_limit = self.default_token_limit

    def enable_limit(self):
        self.reset_token_limit()
        self.reset_history_limit()

    def disable_limit(self):
        self.set_token_limit(0)
        self.set_history_limit(0)

    def add_txt_message(self, role, content):
        self.conversation_txt_history.append({"role": role, "content": content})
        self.manage_txt_history()

    def add_img_message(self, action, content):
        self.conversation_img_history.append(f"{action}: {content}")
        self.manage_img_history()

    def clear_txt_history(self):
        self.conversation_txt_history = []

    def clear_img_history(self):
        self.conversation_img_history = []

    def manage_img_history(self):
        total_tokens = self.estimate_token_count(self.conversation_img_history)
        total_tokens = sum(self.estimate_token_count(message) for message in self.conversation_img_history)
        while total_tokens > self.token_limit:
            if self.conversation_img_history:
                removed_message = self.conversation_img_history.pop(0)
                total_tokens -= self.estimate_token_count(removed_message)
            else:
                break

    def get_manage_txt_history(self):
        return self.conversation_txt_history

    def get_manage_img_history(self):
        return "\n".join(self.conversation_img_history)


if __name__ == "__main__":
    token_manager = TokenManager(20)
    token_manager.add_txt_message("user", "Tell m.")
    print(token_manager.get_manage_txt_history())
