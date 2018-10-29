import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="firstblood",
    version="0.0.1",
    author="sasdf",
    author_email="",
    description="Write exploit faster with up-to-date python 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sasdf/firstblood",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 1 - Planning",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries",
    ],
)
