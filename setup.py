from setuptools import setup
from linpg.scr_core.config import get_current_version,get_author_email,get_short_description,get_repository_url

#读取readme
with open("README.md", "r", encoding="utf-8") as fh: long_description = fh.read()

#生成.whl文件
setup(
    name = "linpg",
    version = get_current_version(),
    author = "Tigeia-Workshop",
    author_email = get_author_email(),
    description = get_short_description(),
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = get_repository_url(),
    license='LICENSE',
    project_urls={
        "Bug Tracker": "https://github.com/Tigeia-Workshop/linpg/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
    ],
    packages=['linpg'],
    include_package_data=True,
    python_requires = '>=3.6',
)
