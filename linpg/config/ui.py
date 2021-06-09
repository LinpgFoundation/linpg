# cython: language_level=3
from .glob import *

_DEFAULT_UI:dict = load_config(os.path.join(os.path.dirname(__file__), "ui.json"))

def get_raw_deault_ui(name:str) -> dict:
    try:
        return deepcopy(_DEFAULT_UI[name])
    except KeyError:
        throw_exception("error", 'The ui called "{}" does not exist!'.format(name))
