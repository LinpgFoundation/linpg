from .pos import *


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
        # 粘贴板内容模块
        from tkinter import Tk

        self.__root = Tk()
        self.__root.withdraw()

    # key是否被按下
    def get_pressed(self, key_name: any) -> bool:
        return pygame.key.get_pressed()[
            self.get_key_code(key_name) if isinstance(key_name, str) else key_name
        ]

    # 获取key的代号
    @staticmethod
    def get_key_code(key_name: str) -> any:
        return pygame.key.key_code(key_name)

    # 获取粘贴板内容
    def get_clipboard(self) -> str:
        return self.__root.clipboard_get()


Key: KeySystem = KeySystem()
