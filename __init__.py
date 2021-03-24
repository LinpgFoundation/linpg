# cython: language_level=3
#加载Zero引擎的必要组件
from .scr_py.dialog import *
try:
    from .scr_py.battle import *
except FileNotFoundError:
    print("Battle system is disabled because some files are missing.")
from .scr_core.tool import *
import platform

print("linpg {0} (pygame {1}, python {2})".format(get_current_version(),pygame.version.ver,platform.python_version()))
print("Hello from the linpg community. http://tjygf.com/forum.php")