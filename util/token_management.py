from util.logger import Logger, logger


class TokenManager:
    def __init__(self):
        token_limit = 0
        history_limit = 0
        self.default_token_limit = token_limit
        self.token_limit = token_limit
        self.default_history_limit = history_limit
        self.history_limit = history_limit
        self.conversation_txt_history = []
        self.conversation_img_history = []

    def estimate_token_count(self, text):
        return len(text)

    def manage_txt_history(self):
        total_tokens = sum(self.estimate_token_count(message['content']) for message in self.conversation_txt_history)
        logger.log('debug', f'request total char count: {total_tokens}')
        while total_tokens > self.token_limit != 0:
            if self.conversation_txt_history:
                removed_message = self.conversation_txt_history.pop(0)
                total_tokens -= self.estimate_token_count(removed_message['content'])
            else:
                break
        while self.history_limit != 0 and len(self.conversation_txt_history) > self.history_limit:
            self.conversation_txt_history.pop(0)

    def set_history_limit(self, count):
        if count is not None:
            self.history_limit = count

    def remove_a_pair_history(self):
        if len(self.get_manage_txt_history()) > 1:
            self.conversation_txt_history.pop()
            self.conversation_txt_history.pop()

    def remove_recent_history(self):
        for i in range(len(self.conversation_txt_history) - 1, -1, -1):
            if self.conversation_txt_history[i].get('recent', False):
                del self.conversation_txt_history[i]

    def sign_history_recent_false(self):
        for i in range(len(self.conversation_txt_history) - 1, -1, -1):
            if self.conversation_txt_history[i].get('recent', False):
                del self.conversation_txt_history[i]['recent']

    def reset_history_limit(self):
        self.history_limit = self.default_history_limit

    def set_token_limit(self, count):
        if count is not None:
            self.token_limit = count

    def reset_token_limit(self):
        self.token_limit = self.default_token_limit

    def enable_limit(self):
        self.reset_token_limit()
        self.reset_history_limit()

    def disable_limit(self):
        self.set_token_limit(0)
        self.set_history_limit(0)

    def add_txt_message(self, role, content, recent = False):
        self.conversation_txt_history.append({"role": role, "content": content, "recent": recent})
        self.manage_txt_history()

    def add_img_message(self, action, content):
        self.conversation_img_history.append(f"{action}: {content}")
        self.manage_img_history()

    def clear_txt_history(self):
        self.conversation_txt_history = []

    def clear_img_history(self):
        self.conversation_img_history = []

    def manage_img_history(self):
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
