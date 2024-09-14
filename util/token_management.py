from config import TOKEN_LIMIT


# Define the token limit (adjust based on the model's context window)

class TokenManager:
    def __init__(self, token_limit = TOKEN_LIMIT):
        self.token_limit = token_limit
        self.conversation_txt_history = []
        self.conversation_img_history = []


    def estimate_token_count(self, text):
        """Estimate the number of tokens in a given text."""
        return len(text) // 4

    def manage_txt_history(self):
        """Trim conversation history to fit within the token limit."""
        total_tokens = sum(self.estimate_token_count(message['content']) for message in self.conversation_txt_history)

        # Trim history if the total token count exceeds the limit
        while total_tokens > self.token_limit:
            if self.conversation_txt_history:
                removed_message = self.conversation_txt_history.pop(0)  # Remove oldest message
                total_tokens -= self.estimate_token_count(removed_message['content'])
            else:
                break

    def add_txt_message(self, role, content):
        """Add a message to the conversation history and manage token limits."""
        self.conversation_txt_history.append({"role": role, "content": content})
        self.manage_txt_history()

    def add_img_message(self, action, content):
        """Add a message to the conversation history and manage token limits."""
        self.conversation_img_history.append(f"{action}: {content}")
        self.manage_img_history()


    def clear_txt_history(self):
        self.conversation_txt_history = []

    def clear_img_history(self):
        self.conversation_img_history = []


    def manage_img_history(self):
        """Trim conversation history to fit within the token limit."""
        total_tokens = self.estimate_token_count(self.conversation_img_history)
        total_tokens = sum(self.estimate_token_count(message) for message in self.conversation_img_history)
        # Trim history if the total token count exceeds the limit
        while total_tokens > self.token_limit:
            if self.conversation_img_history:
                removed_message = self.conversation_img_history.pop(0)  # Remove oldest message
                total_tokens -= self.estimate_token_count(removed_message)
            else:
                break

    def get_manage_txt_history(self):
        return self.conversation_txt_history

    def get_manage_img_history(self):
        return "\n".join(self.conversation_img_history)

    def remove_first_line(self, text):
        # 将字符串按行分割成列表
        lines = text.splitlines()
        # 删除第一行
        if lines:
            lines.pop(0)
        # 重新将列表中的行合并成字符串
        return '\n'.join(lines)

# Example usage
if __name__ == "__main__":
    token_manager = TokenManager(20)
    token_manager.add_txt_message("user", "Tell m.")
    token_manager.add_txt_message("usdfdfder", "Whaikdddddddddddddddfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffdddddddddddddddddddddddddddddddde?")
    print(token_manager.get_manage_txt_history())