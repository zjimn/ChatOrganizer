import json
import time
from api.chat_base_api import ChatBaseApi
from api.ollama_api import OllamaApi
from api.deepbricks_openai_api import DeepBricksOpenai
from api.openai_api import OpenaiApi
from config import constant
from config.constant import OLLAMA_SERVER_KEY, DEEPBRICKS_OPENAI_SERVER_KEY, SILICONFLOW_DEEPSEEK_SERVER_KEY, \
    GENERAL_OPENAI_SERVER_KEY, DEEPSEEK_SERVER_KEY
from exception.chat_request_error import ChatRequestError
from util.config_manager import ConfigManager
from util.logger import logger
from util.text_highlighter import TextHighlighter


class ChatFactory:
    config_manager = ConfigManager()
    def create_model_server(self, model_server_key = None) -> ChatBaseApi:
        if not model_server_key:
            model_server_key = ChatFactory.config_manager.get("model_server_key")
            if not model_server_key:
                raise ValueError(f"请先配置模型服务")
        if model_server_key == OLLAMA_SERVER_KEY:
            return OllamaApi()
        elif model_server_key == DEEPBRICKS_OPENAI_SERVER_KEY:
            return DeepBricksOpenai()
        elif model_server_key in(DEEPSEEK_SERVER_KEY, SILICONFLOW_DEEPSEEK_SERVER_KEY, GENERAL_OPENAI_SERVER_KEY):
            return OpenaiApi()
        else:
            raise ValueError(f"Unknown model server: {model_server_key}")

    def chat_txt(self, prompt, sys_messages, text_widget, interval_ms = 0.05, loading_spinner = None):
        text_highlighter = TextHighlighter(text_widget)
        text_highlighter.clean_bg()
        model_server_key = ChatFactory.config_manager.get("model_server_key")
        stream_output = ChatFactory.config_manager.get("stream_response")
        model_server = self.create_model_server()
        model_server.add_history_message(constant.USER_NAME, prompt, recent = True)
        response = model_server.generate_gpt_completion(prompt, sys_messages, stream_output)
        loading_spinner.stop()
        result = ""
        start_time = time.time()
        is_valid_text = False
        if model_server_key == OLLAMA_SERVER_KEY:
            if not stream_output:
                text_highlighter.follow_insert = False
                logger.log('response', f"API返回文本: {response}")
                if 'message' in response and 'content' in response.message:
                    content = response.message.content
                else:
                    logger.log('error', f"返回数据结构异常\n返回数据: {response}")
                    raise ChatRequestError("返回数据结构异常")
                cancel = model_server.cancel_request_check()
                if cancel:
                    return
                char_list = list(content)
                text_highlighter.batch_insert_word(char_list)
                result = content.strip()
            else:
                text_highlighter.follow_insert = True
                chunks = []
                for chunk in response:
                    chunks.append(chunk)
                    cancel = model_server.cancel_request_check()
                    if cancel:
                        return
                    content = chunk.message.content
                    if not content:
                        continue
                    if not is_valid_text:
                        content = content.lstrip()
                        if content:
                            is_valid_text = True
                    char_list = list(content)
                    text_highlighter.batch_insert_word(char_list)
                    result += content
                    end_time = time.time()
                    total_time = end_time - start_time
                    sleep_time = interval_ms - total_time
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                logger.log('response', f"API返回文本: {chunks}")

        elif model_server_key == DEEPBRICKS_OPENAI_SERVER_KEY:

            result = ""
            if not stream_output:
                text_highlighter.follow_insert = False
                response.raise_for_status()
                response_data = response.json()
                logger.log('response', f"API返回文本: {response_data}")
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0].get('message', {}).get('content', '')
                else:
                    logger.log('warning', "返回数据结构异常")
                    raise ChatRequestError("返回数据结构异常")
                cancel = model_server.cancel_request_check()
                if cancel:
                    return
                char_list = list(content)
                text_highlighter.batch_insert_word(char_list)
                result = content.strip()
            else:
                text_highlighter.follow_insert = True
                single_byte_data = b""
                chunks = b""
                for chunk in response:
                    cancel = model_server.cancel_request_check()
                    if cancel:
                        return
                    start_time = time.time()
                    decoded_data = ""
                    chunks += chunk
                    if b"\ndata" in chunk:
                        index = chunk.index(b"\ndata")
                        byte_str = chunk[0:index]
                        single_byte_data += byte_str
                        byte_json_data = single_byte_data.split(b"data: ")[1]
                        decoded_json_data = byte_json_data.decode()
                        json_object = json.loads(decoded_json_data)
                        single_byte_data = chunk[index:]
                        content = json_object['choices'][0].get('delta').get('content', '')
                        if not content:
                            continue
                        if not is_valid_text:
                            content = content.lstrip()
                            if content:
                                is_valid_text = True
                        char_list = list(content)
                        text_highlighter.batch_insert_word(char_list)
                        end_time = time.time()
                        total_time = end_time - start_time
                        sleep_time = interval_ms - total_time
                        if sleep_time > 0:
                            time.sleep(sleep_time)

                        result += content
                    else:
                        single_byte_data += chunk
                    if "data: [DONE]" in decoded_data:
                        continue
                logger.log('response', f"API返回文本: {chunks}")
        elif model_server_key in [DEEPSEEK_SERVER_KEY, SILICONFLOW_DEEPSEEK_SERVER_KEY, GENERAL_OPENAI_SERVER_KEY]:
            result = ""
            if not stream_output:
                text_highlighter.follow_insert = False
                logger.log('response', f"API返回文本: {response}")
                content = response.choices[0].message.content
                cancel = model_server.cancel_request_check()
                if cancel:
                    return
                if content is not None:
                    char_list = list(content)
                    text_highlighter.batch_insert_word(char_list)
                result = content.strip()
            else:
                text_highlighter.follow_insert = True
                chunks = []
                for chunk in response:
                    chunks.append(chunk)
                    cancel = model_server.cancel_request_check()
                    if cancel:
                        return
                    content = chunk.choices[0].delta.content
                    if not content:
                        continue
                    if not is_valid_text:
                        content = content.lstrip()
                        if content:
                            is_valid_text = True
                    char_list = list(content)
                    text_highlighter.batch_insert_word(char_list)
                    result += content
                    end_time = time.time()
                    total_time = end_time - start_time
                    sleep_time = interval_ms - total_time
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                logger.log('response', f"API返回文本: {chunks}")
        model_server.add_history_message(constant.ASSISTANT_NAME, result, recent=True)
        text_highlighter.insert_word("\n")
        model_server.sign_history_recent_false()
        return result



    def test(self, selected_model_server_key, api_url, api_key, test_model_name):
        model_server = self.create_model_server(selected_model_server_key)
        return model_server.test(api_url, api_key, test_model_name)
