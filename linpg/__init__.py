"""
结构:
exception -> config -> lang -> tools -> basic -> core -> ui -> dialog -> map -> character -> battle -> api
"""
from .api import *
from platform import python_version

print("linpg {0} ({1}, Python {2})".format(Info.get_current_version(), get_library_info(), python_version()))
print("Hello from the linpg community. {}".format(Info.get_repository_url()))
