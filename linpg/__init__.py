"""
结构:
config -> lang -> api -> core -> ui -> dialog -> battle
"""
from .battle import *
import platform

print("linpg {0} (pygame {1}, python {2})".format(get_current_version(),pygame.version.ver,platform.python_version()))
print("Hello from the linpg community. {}".format(get_repository_url()))