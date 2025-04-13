from distutils.core import setup
import os.path
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TikTokApi",
    packages=setuptools.find_packages(),
    version="7.1.0",
    license="MIT",
    description="The Unofficial TikTok API Wrapper in Python 3.",
    author="David Teather",
    author_email="contact.davidteather@gmail.com",
    url="https://github.com/davidteather/tiktok-api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url="https://github.com/davidteather/TikTok-Api/tarball/main",
    keywords=["tiktok", "python3", "api", "unofficial", "tiktok-api", "tiktok api"],
    install_requires=["requests", "playwright", "httpx"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.9",
)
