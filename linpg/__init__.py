"""
结构:
config -> lang -> api -> core -> ui -> dialog -> battle -> interface
"""
from .interface import *
from platform import python_version

print("linpg {0} ({1}, python {2})".format(Info.current_version, get_library_info(), python_version()))
print("Hello from the linpg community. {}".format(Info.repository_url))
