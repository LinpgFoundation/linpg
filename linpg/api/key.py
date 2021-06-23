# cython: language_level=3
from .basic import *
from tkinter import Tk

class KeySystem:
    def __init__(self) -> None:
        self.DOWN = pygame.KEYDOWN
        self.UP = pygame.KEYUP
        self.ESCAPE = pygame.K_ESCAPE
        self.SPACE = pygame.K_SPACE
        self.BACKSPACE = pygame.K_BACKSPACE
        self.DELETE = pygame.K_DELETE
        self.LEFT_CTRL = pygame.K_LCTRL
        self.ARROW_UP = pygame.K_UP
        self.ARROW_DOWN = pygame.K_DOWN
        self.ARROW_LEFT = pygame.K_LEFT
        self.ARROW_RIGHT = pygame.K_RIGHT
        self.RETURN = pygame.K_RETURN
        self.BACKQUOTE = pygame.K_BACKQUOTE
        self.__root = Tk()
        self.__root.withdraw()
    def get_pressed(self, key_name:any) -> bool:
        if isinstance(key_name, str):
            return pygame.key.get_pressed()[self.get_key_code(key_name)]
        else:
            return pygame.key.get_pressed()[key_name]
    def get_key_code(self, key_name:str) -> any: return pygame.key.key_code(key_name)
    def get_clipboard(self) -> str: return self.__root.clipboard_get()

KEY = KeySystem()
