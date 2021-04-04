from setuptools import setup
import linpg

#读取readme
with open("README.md", "r", encoding="utf-8") as fh: long_description = fh.read()

#生成.whl文件
setup(
    name = "linpg",
    version = linpg.get_current_version(),
    author = "Tigeia-Workshop",
    author_email = linpg.get_author_email(),
    description = linpg.get_short_description(),
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = linpg.get_repository_url(),
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
    install_requires = [
        "pygame",
        "pyyaml",
        "pyav",
        "numpy",
    ]
)
