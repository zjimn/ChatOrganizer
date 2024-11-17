class PreferenceReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.preferences = {}
        self._load_preferences()

    def _load_preferences(self):
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    # 忽略注释行和空行
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue
                    # 解析键值对
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.preferences[key.strip()] = self._parse_value(value.strip())
        except FileNotFoundError:
            print(f"配置文件 {self.file_path} 未找到。")
        except Exception as e:
            print(f"加载配置文件时出错: {e}")

    def _parse_value(self, value):
        try:
            return int(value)
        except ValueError:
            return value

    def get(self, key, default=None):
        return self.preferences.get(key, default)

    def __str__(self):
        return str(self.preferences)


# 示例用法
if __name__ == "__main__":
    reader = PreferenceReader("../preference.properties")
    print("TOKEN_LIMIT:", reader.get("TOKEN_LIMIT", 0))
    print("TYPEWRITER_EFFECT:", reader.get("TYPEWRITER_EFFECT", 0))