from abc import ABC
from typing import Any, Sequence

from ..exception import Exceptions


class TypeSafeSetter(ABC):
    # 根据keys查找被设置对应对应对象为指定值
    @staticmethod
    def set_by_keys(_dict: dict, _keys: Sequence, value: object, assumeKeyExists: bool = True) -> None:
        if len(_keys) < 1:
            Exceptions.fatal("Keys' length has to be greater than 0.")
        pointer: dict = _dict
        last_key_index: int = len(_keys) - 1
        for index in range(last_key_index):
            _item: object | None = pointer.get(_keys[index])
            if isinstance(_item, dict):
                pointer = _item
            elif _item is None:
                if assumeKeyExists is True:
                    Exceptions.fatal(f'Getting "KeyError" while trying to set keys {_keys} to dict!')
                pointer[_keys[index]] = {}
                pointer = pointer[_keys[index]]
            else:
                Exceptions.fatal(f"Getting not dict object {_item} while trying to set keys {_keys} to dict!")
        pointer[_keys[last_key_index]] = value

    # 获取static数据字典 (子类需实现)
    @classmethod
    def _get_data(cls) -> dict:
        Exceptions.fatal("_get_data()", 1)

    # 设置特定的数据
    @classmethod
    def set(cls, *_key: str, value: Any, assumeKeyExists: bool = True) -> None:
        cls.set_by_keys(cls._get_data(), _key, value, assumeKeyExists)

    # 清空所有数据（谨慎使用）
    @classmethod
    def clear(cls) -> None:
        cls._get_data().clear()
