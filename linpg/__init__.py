from .dialogue import *


def init() -> None:
    pygame.init()
    Languages.reload()
    Variables.Persistent.reload()
    Controller.update()
    LINPG_RESERVED_CHANNELS.init()


# print linpg information
print(
    f'linpg {Version.get_full()} ({f"{GraphicLibrary.get_name()} {pygame.version.ver}"}, Python {Exceptions.get_python_version()})'
)
# only show prompt when using pygame
if GraphicLibrary.is_using_pygame():
    print("Hello from the linpg community. https://github.com/LinpgFoundation/linpg")
