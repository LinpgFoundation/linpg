import copy
from abc import ABC
from functools import reduce
from operator import getitem
from typing import Any, Final, Sequence

from ..exception import Exceptions


class TypeSafeGetter(ABC):
    __RETURN_NONE_FOR_KEY_ERROR: Final[str] = "<!RETURN_NONE_FOR_KEY_ERROR>"

    # if data contains key
    @classmethod
    def contains(cls, key: Any) -> bool:
        return key in cls._get_data()

    # 根据keys查找值，最后返回一个复制的对象
    @classmethod
    def get_by_keys(cls, _dict: dict, _keys: Sequence, _default: Any | None = None, _deepcopy: bool = True) -> Any:
        try:
            return copy.deepcopy(reduce(getitem, _keys, _dict)) if _deepcopy is True else reduce(getitem, _keys, _dict)
        except KeyError:
            if _default is None:
                Exceptions.fatal(f'Getting "KeyError" while trying to get keys {_keys} from dict!')
            return _default if _default is not cls.__RETURN_NONE_FOR_KEY_ERROR else None

    # 获取特定的数据
    @classmethod
    def keys(cls) -> tuple:
        return tuple(cls._get_data().keys())

    # 获取static数据字典 (子类需实现)
    @classmethod
    def _get_data(cls) -> dict:
        Exceptions.fatal("_get_data()", 1)

    # 获取特定的数据
    @classmethod
    def get(cls, *_key: Any, _deepcopy: bool = True) -> Any:
        return cls.get_by_keys(cls._get_data(), _key, _deepcopy=_deepcopy)

    # 尝试获取特定的数据
    @classmethod
    def try_get(cls, *_key: Any, _default: Any | None = None, _deepcopy: bool = True) -> Any | None:
        return cls.get_by_keys(cls._get_data(), _key, _default, _deepcopy)

    # 是否值存在且不为None
    @classmethod
    def exists_not_none(cls, *_key: Any) -> bool:
        return cls.try_get(*_key, _default=cls.__RETURN_NONE_FOR_KEY_ERROR) is not None

    # 以str的形式获取特定的数据
    @classmethod
    def get_str(cls, *_key: Any) -> str:
        return str(cls.get(*_key))

    # 尝试以str的形式获取特定的数据
    @classmethod
    def try_get_str(cls, *_key: Any) -> str | None:
        _temp: Any | None = cls.try_get(*_key, _default=cls.__RETURN_NONE_FOR_KEY_ERROR)
        return str(_temp) if _temp is not None else _temp

    # 以int的形式获取特定的数据
    @classmethod
    def get_int(cls, *_key: Any) -> int:
        return int(cls.get(*_key))

    # 尝试以int的形式获取特定的数据
    @classmethod
    def try_get_int(cls, *_key: Any) -> int | None:
        _temp: Any | None = cls.try_get(*_key, _default=cls.__RETURN_NONE_FOR_KEY_ERROR)
        return int(_temp) if _temp is not None else _temp

    # 以bool的形式获取特定的数据
    @classmethod
    def get_bool(cls, *_key: Any) -> bool:
        return bool(cls.get(*_key))

    # 尝试以bool的形式获取特定的数据
    @classmethod
    def try_get_bool(cls, *_key: Any) -> bool | None:
        _temp: Any | None = cls.try_get(*_key, _default=cls.__RETURN_NONE_FOR_KEY_ERROR)
        return bool(_temp) if _temp is not None else _temp

    # 以dict的形式获取特定的数据
    @classmethod
    def get_dict(cls, *_key: Any) -> dict:
        return dict(cls.get(*_key))

    # 以dict的形式获取特定的数据（不复制）
    @classmethod
    def get_dict_ref(cls, *_key: Any) -> dict:
        return dict(cls.get(*_key, _deepcopy=False))

    # 尝试以dict的形式获取特定的数据
    @classmethod
    def try_get_dict(cls, *_key: Any) -> dict | None:
        _temp: Any | None = cls.try_get(*_key, _default=cls.__RETURN_NONE_FOR_KEY_ERROR)
        return dict(_temp) if _temp is not None else _temp

    # 以list的形式获取特定的数据
    @classmethod
    def get_list(cls, *_key: Any) -> list:
        return list(cls.get(*_key))

    # 尝试以list的形式获取特定的数据
    @classmethod
    def try_get_list(cls, *_key: Any) -> list | None:
        _temp: Any | None = cls.try_get(*_key, _default=cls.__RETURN_NONE_FOR_KEY_ERROR)
        return list(_temp) if _temp is not None else _temp

    # 以tuple的形式获取特定的数据
    @classmethod
    def get_tuple(cls, *_key: Any) -> tuple:
        return tuple(cls.get(*_key))

    # 尝试以tuple的形式获取特定的数据
    @classmethod
    def try_get_tuple(cls, *_key: Any) -> tuple | None:
        _temp: Any | None = cls.try_get(*_key, _default=cls.__RETURN_NONE_FOR_KEY_ERROR)
        return tuple(_temp) if _temp is not None else _temp
