# cython: language_level=3
#加载Zero引擎的必要组件
from .scr_py.dialog import *
from .scr_py.battle import *
from .scr_py.mapCreator import *
from .scr_py.experimental import *
import platform

print("Zero Engine 3 (pygame {}, python {})".format(pygame.version.ver,platform.python_version()))
print("Hello from the zero engine community. http://tjygf.com/forum.php")