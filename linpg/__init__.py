"""
结构:
exception -> config -> lang -> tools -> basic -> core -> ui -> dialog -> battle -> api
"""
from .api import *
from platform import python_version

print("linpg {0} ({1}, Python {2})".format(Info.current_version, get_library_info(), python_version()))
print("Hello from the linpg community. {}".format(Info.repository_url))
