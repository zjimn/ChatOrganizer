import re


def get_chars_by_count(text, count=50):
    if text is None:
        return ""
    # 将所有的换行符替换为空格，去掉空白行
    text = re.sub(r'\s*\n\s*', ' ', text)
    # 使用正则表达式替换连续的多个空格为一个空格
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:count]