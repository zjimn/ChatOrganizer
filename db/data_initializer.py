from config.constant import OLLAMA_SERVER_NAME, OLLAMA_SERVER_KEY, \
    DEEPBRICKS_OPENAI_SERVER_KEY, DEEPBRICKS_SERVER_NAME, OLLAMA_DEFAULT_URL, SILICONFLOW_DEEPSEEK_SERVER_KEY, \
    SILICONFLOW_DEEPSEEK_SERVER_NAME, \
    DEEPBRICKS_OPENAI_DEFAULT_URL, DEEPSEEK_DEFAULT_URL, GENERAL_OPENAI_SERVER_NAME, GENERAL_OPENAI_SERVER_KEY, \
    DEEPSEEK_SERVER_KEY, DEEPSEEK_SERVER_NAME, SILICONFLOW_DEEPSEEK_DEFAULT_URL
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
        self.default_deepseek_txt_model_id = None
        self.default_siliconflow_deepseek_txt_model_id = None
        self.default_deepbricks_openai_txt_model_id = None
        self.default_deepbricks_openai_img_model_id = None
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
        self.insert_model_server_data()
        self.insert_model_server_detail_data()

    def insert_model_server_data(self):
        try:
            exists = self.msa.has_data()
            if not exists:
                self.msa.insert(DEEPSEEK_SERVER_KEY, DEEPSEEK_SERVER_NAME, True, True)
                self.msa.insert(SILICONFLOW_DEEPSEEK_SERVER_KEY, SILICONFLOW_DEEPSEEK_SERVER_NAME, True, True)
                self.msa.insert(OLLAMA_SERVER_KEY, OLLAMA_SERVER_NAME, True, False)
                self.msa.insert(DEEPBRICKS_OPENAI_SERVER_KEY, DEEPBRICKS_SERVER_NAME, True, True)
                self.msa.insert(GENERAL_OPENAI_SERVER_KEY, GENERAL_OPENAI_SERVER_NAME, True, True)
        except Exception as e:
            logger.log('error', f"insert default model server data error: {e}")


    def insert_model_server_detail_data(self):
        try:
            exists = self.msda.has_data()
            if not exists:
                self.msda.upsert(OLLAMA_SERVER_KEY, api_url=OLLAMA_DEFAULT_URL)
                self.msda.upsert(DEEPSEEK_SERVER_KEY, api_url=DEEPSEEK_DEFAULT_URL, api_key="sk-8b6087e0c8f44eeea187fa69ece85c6a", txt_model_id=self.default_deepseek_txt_model_id)
                self.msda.upsert(SILICONFLOW_DEEPSEEK_SERVER_KEY, api_url=SILICONFLOW_DEEPSEEK_DEFAULT_URL, api_key="sk-ffislvethfycripbdlvkrckaremozxwnrxjvwobulovevoep", txt_model_id=self.default_siliconflow_deepseek_txt_model_id)
                self.msda.upsert(DEEPBRICKS_OPENAI_SERVER_KEY, api_url=DEEPBRICKS_OPENAI_DEFAULT_URL, api_key="sk-uvvuoMaVh3uTK0FlgBXrcNJcoLhJcS7p12aBV0U4al1so2Qg", txt_model_id=self.default_deepbricks_openai_txt_model_id, img_model_id=self.default_deepbricks_openai_img_model_id)
        except Exception as e:
            logger.log('error', f"insert default model server data error: {e}")

    def insert_default_model(self):
        try:
            with self.dma as dma:
                exist = dma.has_data()
                if not exist:
                    dma.insert_data("GPT-4o-2024-08-06", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    dma.insert_data("GPT-4o", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    dma.insert_data("o1-mini", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    dma.insert_data("o1-preview", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    dma.insert_data("GPT-4-turbo", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    dma.insert_data("Claude-3.5-Sonnet", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    dma.insert_data("GPT-4o-mini", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    self.default_deepbricks_openai_txt_model_id = dma.insert_data("GPT-3.5-turbo", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    dma.insert_data("GPT-3.5-turbo-instruct", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    dma.insert_data("LLama-3.1-405b", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    dma.insert_data("LLama-3.1-70b", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    dma.insert_data("LLama-3-70b", "txt", DEEPBRICKS_OPENAI_SERVER_KEY)
                    self.default_deepbricks_openai_img_model_id = dma.insert_data("dall-e-3", "img", DEEPBRICKS_OPENAI_SERVER_KEY)
                    logger.log('info', "insert default dialogue model data")

                    dma.insert_data("deepseek-reasoner", "txt", DEEPSEEK_SERVER_KEY, "deepseek-r1")
                    self.default_deepseek_txt_model_id = dma.insert_data("deepseek-chat", "txt", DEEPSEEK_SERVER_KEY)

                    dma.insert_data("deepseek-ai/DeepSeek-R1", "txt", SILICONFLOW_DEEPSEEK_SERVER_KEY)
                    dma.insert_data("deepseek-ai/DeepSeek-V3", "txt", SILICONFLOW_DEEPSEEK_SERVER_KEY)
                    dma.insert_data("deepseek-ai/DeepSeek-R1-Distill-Llama-70B", "txt", SILICONFLOW_DEEPSEEK_SERVER_KEY)
                    dma.insert_data("deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", "txt", SILICONFLOW_DEEPSEEK_SERVER_KEY)
                    dma.insert_data("deepseek-ai/DeepSeek-R1-Distill-Qwen-14B", "txt", SILICONFLOW_DEEPSEEK_SERVER_KEY)
                    dma.insert_data("deepseek-ai/DeepSeek-R1-Distill-Llama-8B", "txt", SILICONFLOW_DEEPSEEK_SERVER_KEY)
                    dma.insert_data("deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", "txt", SILICONFLOW_DEEPSEEK_SERVER_KEY)
                    self.default_siliconflow_deepseek_txt_model_id = dma.insert_data("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "txt", SILICONFLOW_DEEPSEEK_SERVER_KEY, "免费")
                    dma.insert_data("deepseek-ai/DeepSeek-V2.5", "txt", SILICONFLOW_DEEPSEEK_SERVER_KEY, "免费")

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
        data = [{"name":"Java编程助手","content":"你是一个Java编程助手。你的角色是帮助编写、调试和解释Java代码。如果用户提供了编程问题或错误信息，你将提供解决方案、解释和建议来改进代码。"},{"name":"C++编程助手","content":"你是一个C++编程助手。你的角色是帮助编写、调试和解释C++代码。如果用户提供了编程问题或错误信息，你将提供解决方案、解释和建议来改进代码。"},{"name":"Python编程助手","content":"你是一个Python编程助手。你的角色是帮助编写、调试和解释Python代码。如果用户提供了编程问题或错误信息，你将提供解决方案、解释和建议来改进代码。"},{"name":"翻译助手（英文到中文）","content":"你是一个翻译助手。你的任务是将英文文本准确流利地翻译成中文。请确保翻译传达原文的意思，并且中文表达自然。如果文本较复杂，请提供符合上下文的翻译。"},{"name":"翻译助手（中文到英文）","content":"你是一个翻译助手。你的任务是将中文文本准确流利地翻译成英文。请确保翻译传达原文的意思，并且英文表达自然。如果文本较复杂，请提供符合上下文的翻译。"},{"name":"Houdini特效制作助手","content":"你是一个Houdini特效制作助手。你的任务是帮助用户使用Houdini软件创建视觉特效。提供特效制作的步骤、技巧和优化建议，帮助用户理解节点操作、粒子系统、动力学模拟、渲染设置等方面。协助调试效果和提高特效的表现质量。"},{"name":"写作助手","content":"你是一个写作助手。你的任务是帮助改进写作，建议语法修正、风格优化，并提供替代句式，使文章更加简洁、清晰且吸引人。重点提升文章的可读性和表达效果，但不改变原意。"},{"name":"对话助手","content":"你是一个对话助手。你的任务是与用户进行自然的、富有互动的对话。保持友好的语气，回答问题，并使对话流畅自然，同时提供有帮助和信息性的内容。"}, {"name": "会计助手", "content": "你是一个金蝶财务云的会计助手，专门帮助用户处理财务和会计相关事务。你的角色包括解答会计准则、财务报表、税务申报、账务处理等方面的问题，帮助用户高效完成财务工作。"}]
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



