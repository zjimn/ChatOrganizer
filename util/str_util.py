import re


def get_chars_by_count(text, count=50):
    if text is None:
        return ""
    text = re.sub(r'\s*\n\s*', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:count]
