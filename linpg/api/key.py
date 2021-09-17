from .coordinate import *


class KeySystem:

    # 按键常量
    DOWN: int = pygame.KEYDOWN
    UP: int = pygame.KEYUP
    ESCAPE: int = pygame.K_ESCAPE
    SPACE: int = pygame.K_SPACE
    BACKSPACE: int = pygame.K_BACKSPACE
    DELETE: int = pygame.K_DELETE
    LEFT_CTRL: int = pygame.K_LCTRL
    ARROW_UP: int = pygame.K_UP
    ARROW_DOWN: int = pygame.K_DOWN
    ARROW_LEFT: int = pygame.K_LEFT
    ARROW_RIGHT: int = pygame.K_RIGHT
    RETURN: int = pygame.K_RETURN
    BACKQUOTE: int = pygame.K_BACKQUOTE
    F3: int = pygame.K_F3

    # 粘贴板内容模块
    from tkinter import Tk

    __root: Tk = Tk()
    __root.withdraw()

    # key是否被按下
    def get_pressed(self, key_name: any) -> bool:
        return pygame.key.get_pressed()[self.get_key_code(key_name) if isinstance(key_name, str) else key_name]

    # 获取key的代号
    @staticmethod
    def get_key_code(key_name: str) -> any:
        return pygame.key.key_code(key_name)

    # 获取粘贴板内容
    def get_clipboard(self) -> str:
        return self.__root.clipboard_get()


Key: KeySystem = KeySystem()
