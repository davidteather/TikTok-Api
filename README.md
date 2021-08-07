
# Unofficial TikTok API in Python

This is an unofficial api wrapper for TikTok.com in python. With this api you are able to call most trending and fetch specific user information as well as much more.

 [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&style=flat-square)](https://www.linkedin.com/in/davidteather/) [![Sponsor Me](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub)](https://github.com/sponsors/davidteather)  [![GitHub release (latest by date)](https://img.shields.io/github/v/release/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/releases) [![Build Status](https://img.shields.io/github/workflow/status/davidteather/tiktok-api/TikTokApi%20CI/master)](https://github.com/davidteather/TikTok-Api/actions/workflows/package-test.yml) [![GitHub](https://img.shields.io/github/license/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/blob/master/LICENSE) [![Downloads](https://pepy.tech/badge/tiktokapi)](https://pypi.org/project/TikTokApi/) ![](https://visitor-badge.laobi.icu/badge?page_id=davidteather.TikTok-Api) [![Support Server](https://img.shields.io/discord/783108952111579166.svg?color=7289da&logo=discord&style=flat-square)](https://discord.gg/yyPhbfma6f)

## Thank you to our sponsors & advertisers

[![TikAPI](imgs/logo128.png)](https://tikapi.io/?ref=davidteather)   |  **[TikAPI](https://tikapi.io/?ref=davidteather)** is a paid TikTok API service providing an full out-of-the-box solution for developers, trusted by 100+ companies. [Learn more](https://tikapi.io/?ref=davidteather)
:-------------------------:|:-------------------------:

## Table of Contents
- [Getting Started](#getting-started)
    - [Installing](#installing)
    - [Common Issues](#common-issues)
- [Quick Start Guide](#quick-start-guide)
    - [Examples](https://github.com/davidteather/TikTok-Api/tree/master/examples)
- [Documentation](#documentation)
- [Built With](#built-with)
- [Authors](#authors)
- [License](#license)

## Getting Started

To get started using this api follow the instructions below.

#### How to support the project
* Feel free to sponsor me on GitHub
* Feel free to tip the project using the brave browser
* Submit PRs for issues :)

### Installing

If you run into an issue please check the closed issues on the github. You're most likely not the first person to experience this issue. If nothing works feel free to open an issue.

```sh
pip install TikTokApi
python -m playwright install
```
If you would prefer a video walk through of setting up this package I created a [YouTube video](https://www.youtube.com/watch?v=zwLmLfVI-VQ) just for that.



If you're on MacOS you may need to install [XCode Developer Tools](https://webkit.org/build-tools/)

#### Docker Installation

Clone this repository onto a local machine then run the following commands.

```sh
docker build . -t tiktokapi:latest
docker run -v TikTokApi --rm tiktokapi:latest python3 your_script.py
```

**Note** this assumes your script is named your_script.py and lives in the root of this directory.

### Common Issues

Please don't open an issue if you're experiencing one of these just comment if the provided solution do not work for you.

* **Browser Has no Attribute** - make sure you ran `python3 -m playwright install`, if your error persists try the [playwright](https://github.com/microsoft/playwright-python) quickstart guide and diagnose issues from there.

## Quick Start Guide

Here's a quick bit of code to get the most recent trending on TikTok. There's more examples in the examples directory.

```py
from TikTokApi import TikTokApi
api = TikTokApi.get_instance()
results = 10

# Since TikTok changed their API you need to use the custom_verifyFp option. 
# In your web browser you will need to go to TikTok, Log in and get the s_v_web_id value.
trending = api.by_trending(count=results, custom_verifyFp="")

for tiktok in trending:
    # Prints the id of the tiktok
    print(tiktok['id'])

print(len(trending))
```

To run the example scripts from the repository root, make sure you use the
module form of python the interpreter

```sh
python -m examples.get_trending
```

[Here's](https://gist.github.com/davidteather/7c30780bbc30772ba11ec9e0b909e99d) an example of what a TikTok dictionary looks like.

## Documentation

You can find the documentation [here](https://davidteather.github.io/TikTok-Api/docs/TikTokApi.html) (you'll likely just need the TikTokApi section of the docs), I will be making this documentation more complete overtime as it's not super great right now, but better than just having it in the readme!

## Authors

* **David Teather** - *Initial work* - [davidteather](https://github.com/davidteather)

See also the list of [contributors](https://github.com/davidteather/TikTok-Api/contributors) who participated in this project.

## License

This project is licensed under the MIT License