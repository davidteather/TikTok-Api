import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="unoffical-tiktok-api",
    version="0.1",
    author="David Teather",
    author_email="dteather0@gmail.com",
    description="Unoffical tiktok api wrapper in python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davidteather/TikTok-Api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)