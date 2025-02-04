from config.constant import OLLAMA_SERVER_NAME, OLLAMA_SERVER_KEY, \
    OPENAI_SERVER_KEY, OPENAI_SERVER_NAME, OLLAMA_DEFAULT_URL, DEEPSEEK_SERVER_KEY, DEEPSEEK_SERVER_NAME
from db.content_hierarchy_access import ContentHierarchyDataAccess
from db.dialogue_model_access import DialogueModelAccess
from db.dialogue_preset_access import DialoguePresetAccess
from db.dialogue_preset_detail_access import DialoguePresetDetailAccess
from db.model_server_access import ModelServerAccess
from db.model_server_detail_access import ModelServerDetailAccess
from util.config_manager import ConfigManager
from util.logger import logger


class DataInitializer:
    def __init__(self):
        self.default_txt_model_id = None
        self.default_img_model_id = None
        self.chda = ContentHierarchyDataAccess()
        self.msa = ModelServerAccess()
        self.msda = ModelServerDetailAccess()
        self.dma = DialogueModelAccess()
        self.dpa = DialoguePresetAccess()
        self.dpda = DialoguePresetDetailAccess()
        self.config_manager = ConfigManager()

    def insert_default_content_hierarchy(self):
        try:
            with self.chda as chda:
                exist = chda.has_data()
                if not exist:
                    chda.insert_data(None, 0, "root", 0)
                    logger.log('info', f"insert default content hierarchy data")
                else:
                    pass
        except Exception as e:
            logger.log('error', f"insert default content hierarchy data error: {e}")

    def insert_default_data(self):
        self.insert_dialog_model_data()
        self.insert_model_server_data()
        self.insert_model_server_detail_data()

    def insert_dialog_model_data(self):
        try:
            if self.default_txt_model_id:
                self.config_manager.set("txt_model_id", self.default_txt_model_id)
                self.config_manager.set("txt_model_name", "GPT-3.5-turbo")
            if self.default_img_model_id:
                self.config_manager.set("img_model_id", self.default_img_model_id)
                self.config_manager.set("img_model_name", "dall-e-3")
            self.config_manager.set("model_server", OPENAI_SERVER_KEY)
        except Exception as e:
            logger.log('error', f"insert default config data error: {e}")

    def insert_model_server_data(self):
        try:
            exists = self.msa.has_data()
            if not exists:
                self.msa.insert(DEEPSEEK_SERVER_KEY, DEEPSEEK_SERVER_NAME)
                self.msa.insert(OLLAMA_SERVER_KEY, OLLAMA_SERVER_NAME)
                self.msa.insert(OPENAI_SERVER_KEY, OPENAI_SERVER_NAME)
        except Exception as e:
            logger.log('error', f"insert default model server data error: {e}")


    def insert_model_server_detail_data(self):
        try:
            exists = self.msda.has_data()
            if not exists:
                self.msda.upsert(OLLAMA_SERVER_KEY, api_url=OLLAMA_DEFAULT_URL)
                self.msda.upsert(OPENAI_SERVER_KEY, txt_model_id=self.default_txt_model_id, img_model_id=self.default_img_model_id)
        except Exception as e:
            logger.log('error', f"insert default model server data error: {e}")

    def insert_default_model(self):
        try:
            with self.dma as dma:
                exist = dma.has_data()
                if not exist:
                    dma.insert_data("GPT-4o-2024-08-06", "txt", OPENAI_SERVER_KEY)
                    dma.insert_data("GPT-4o", "txt", OPENAI_SERVER_KEY)
                    dma.insert_data("o1-mini", "txt", OPENAI_SERVER_KEY)
                    dma.insert_data("o1-preview", "txt", OPENAI_SERVER_KEY)
                    dma.insert_data("GPT-4-turbo", "txt", OPENAI_SERVER_KEY)
                    dma.insert_data("Claude-3.5-Sonnet", "txt", OPENAI_SERVER_KEY)
                    dma.insert_data("GPT-4o-mini", "txt", OPENAI_SERVER_KEY)
                    self.default_txt_model_id = dma.insert_data("GPT-3.5-turbo", "txt", OPENAI_SERVER_KEY)
                    dma.insert_data("GPT-3.5-turbo-instruct", "txt", OPENAI_SERVER_KEY)
                    dma.insert_data("LLama-3.1-405b", "txt", OPENAI_SERVER_KEY)
                    dma.insert_data("LLama-3.1-70b", "txt", OPENAI_SERVER_KEY)
                    dma.insert_data("LLama-3-70b", "txt", OPENAI_SERVER_KEY)
                    self.default_img_model_id = dma.insert_data("dall-e-3", "img", OPENAI_SERVER_KEY)
                    logger.log('info', "insert default dialogue model data")
                else:
                    pass
        except Exception as e:
            logger.log('error', f"insert default dialogue model data error: {e}")

    def initialize(self):
        self.insert_default_content_hierarchy()
        self.insert_default_model()
        self.insert_default_data()
        self.insert_default_preset()

    def insert_default_preset(self):
        data = [{"name":"翻译助手（英文到中文）","content":"你是一个翻译助手。你的任务是将英文文本准确流利地翻译成中文。请确保翻译传达原文的意思，并且中文表达自然。如果文本较复杂，请提供符合上下文的翻译。"},{"name":"翻译助手（中文到英文）","content":"你是一个翻译助手。你的任务是将中文文本准确流利地翻译成英文。请确保翻译传达原文的意思，并且英文表达自然。如果文本较复杂，请提供符合上下文的翻译。"},{"name":"Houdini特效制作助手","content":"你是一个Houdini特效制作助手。你的任务是帮助用户使用Houdini软件创建视觉特效。提供特效制作的步骤、技巧和优化建议，帮助用户理解节点操作、粒子系统、动力学模拟、渲染设置等方面。协助调试效果和提高特效的表现质量。"},{"name":"Python编程助手","content":"你是一个Python编程助手。你的角色是帮助编写、调试和解释Python代码。如果用户提供了编程问题或错误信息，你将提供解决方案、解释和建议来改进代码。"},{"name":"写作助手","content":"你是一个写作助手。你的任务是帮助改进写作，建议语法修正、风格优化，并提供替代句式，使文章更加简洁、清晰且吸引人。重点提升文章的可读性和表达效果，但不改变原意。"},{"name":"数学辅导员","content":"你是一个数学辅导员。你的角色是帮助用户理解和解决数学问题。提供详细的解题步骤，并确保用户理解背后的数学概念。必要时提供提示和替代方法。"},{"name":"情感支持助手","content":"你是一个情感支持助手。你的角色是提供理解和共情的回应。当用户分享感受或寻求建议时，提供鼓励和支持。保持耐心和无偏见，给予用户一个安全的聊天空间。"},{"name":"英文语法助手","content":"你是一个英文语法助手。你的任务是纠正文本中的语法、标点和拼写错误，并提供改进句子结构、用词选择和整体可读性的建议。"},{"name":"健康顾问","content":"你是一个健康顾问，提供关于常见健康问题的信息和指导。提供基于证据的建议，但始终提醒用户，针对具体的健康问题，咨询医生或专业医疗提供者是最佳选择。"},{"name":"历史助手","content":"你是一个历史助手。你的任务是回答有关历史事件、人物和时期的问题。提供事实性、客观的回答，并通过清晰的解释帮助用户理解历史的意义。"},{"name":"旅行助手","content":"你是一个旅行助手。你的角色是根据用户的需求提供旅行推荐，包括目的地、活动和小贴士。考虑预算、气候和兴趣等因素，提供个性化的旅行建议。"},{"name":"对话助手","content":"你是一个对话助手。你的任务是与用户进行自然的、富有互动的对话。保持友好的语气，回答问题，并使对话流畅自然，同时提供有帮助和信息性的内容。"},{"name":"购物助手","content":"你是一个购物助手。你的角色是根据用户的需求帮助选择最佳产品。通过询问相关问题了解用户的偏好，提供产品对比，并推荐符合需求和预算的选择。"},{"name":"职业顾问","content":"你是一个职业顾问。你的任务是帮助用户探索职业路径、提升简历、准备面试，并提供求职和职业发展的建议。确保建议符合用户的技能、兴趣和职业目标。"}]
        with self.dpa as dpa:
            try:
                exist = dpa.has_data()
                if not exist:
                    for item in data:
                        name = item["name"]
                        content = item["content"]
                        pid = dpa.insert_data(name, 0)
                        with self.dpda as dpda:
                            dpda.insert_data(pid, content)
                    logger.log('info', "insert default dialogue preset data")
                else:
                    pass
            except Exception as e:
                logger.log('error', f"insert dialogue preset data error: {e}")



