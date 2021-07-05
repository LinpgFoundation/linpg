# cython: language_level=3
from .glob import *

_DEFAULT_UI:dict = Config.load_internal("ui.json")

def get_raw_deault_ui(name:str) -> dict:
    try:
        return deepcopy(_DEFAULT_UI[name])
    except KeyError:
        EXCEPTION.throw("error", 'The ui called "{}" does not exist!'.format(name))
