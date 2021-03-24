import setuptools
from .scr_core.config import *

try:
    with open("README.md", "r", encoding="utf-8") as fh: long_description = fh.read()
except:
    long_description = ""

#生成.whl文件
setuptools.setup(
    name = "linpg",
    version = get_current_version(),
    author = "Tigeia-Workshop",
    author_email = get_author_email(),
    description = get_short_description(),
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = get_repository_url(),
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
    ],
    package_dir={"": "src"},
    python_requires = '>=3.6',
)
