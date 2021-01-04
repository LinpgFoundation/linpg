import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

#生成.whl文件
setuptools.setup(
    name="linpg", # Replace with your own username
    version="3.0.dev1",
    author="yudonglin",
    author_email="yudong9912@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)
