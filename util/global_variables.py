
class GlobalVariables:
    _global_dict = {}

    @classmethod
    def set(cls, key, value):
        cls._global_dict[key] = value

    @classmethod
    def get(cls, key, default=None):
        return cls._global_dict.get(key, default)

    @classmethod
    def delete(cls, key):
        if key in cls._global_dict:
            del cls._global_dict[key]

    @classmethod
    def clear(cls):
        cls._global_dict.clear()

    @classmethod
    def keys(cls):
        return list(cls._global_dict.keys())

    @classmethod
    def values(cls):
        return list(cls._global_dict.values())

    @classmethod
    def get_global_dict(cls):
        return cls._global_dict

