from .level import *


def init() -> None:
    GraphicLibrary.init()
    Languages.reload()
    Variables.Persistent.reload()
    Controller.update()
    LINPG_RESERVED_CHANNELS.init()


config = Configurations
display = Display
colors = Colors
coordinates = Coordinates
controller = Controller
images = Images

# print linpg information
print(f'linpg {Version.get_full()} ({f"{GraphicLibrary.get_full()}"}, Python {Exceptions.get_python_version()})')

# only show prompt when using pygame (not ce)
if GraphicLibrary.is_using_pygame():
    print("Hello from the linpg community. https://github.com/LinpgFoundation/linpg")
