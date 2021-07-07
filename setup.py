import json
import os
import setuptools

#读取信息
info_json_path:str = "info.json"
if not os.path.exists(info_json_path): info_json_path = os.path.join("src", "linpg", "config", "info.json")
with open(info_json_path, "r", encoding='utf-8') as f:
    Data = json.load(f)
    INFO:dict = {
        "version": "{0}.{1}.{2}".format(Data["version"], Data["revision"], Data["patch"]),
        "author_email": Data["author_email"],
        "description": Data["short_description"],
        "url": Data["repository_url"]
    }

#读取readme
with open("README.md", "r", encoding="utf-8") as fh: long_description = fh.read()

#生成.whl文件
setuptools.setup(
    name = "linpg",
    version = INFO["version"],
    author = "Tigeia-Workshop",
    author_email = INFO["author_email"],
    description = INFO["description"],
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = INFO["url"],
    license='LICENSE',
    project_urls={
        "Bug Tracker": "https://github.com/Tigeia-Workshop/linpg/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
    ],
    package_dir={"": "src"},
    include_package_data=True,
    packages=setuptools.find_packages(where="src"),
    python_requires = '>=3.9',
    install_requires = [
        "linpgtoolkit",
        "pygame",
        "pyyaml",
        "av",
        "numpy",
    ]
)
