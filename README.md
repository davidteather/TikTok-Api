# Unofficial TikTok API in Python

This is an unofficial api wrapper for TikTok.com in python. With this api you are able to call most trending and fetch specific user information as well as much more.

[![DOI](https://zenodo.org/badge/188710490.svg)](https://zenodo.org/badge/latestdoi/188710490) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&style=flat-square)](https://www.linkedin.com/in/davidteather/) [![Sponsor Me](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub)](https://github.com/sponsors/davidteather) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/releases) [![GitHub](https://img.shields.io/github/license/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/blob/main/LICENSE) [![Downloads](https://pepy.tech/badge/tiktokapi)](https://pypi.org/project/TikTokApi/) ![](https://visitor-badge.laobi.icu/badge?page_id=davidteather.TikTok-Api) [![Support Server](https://img.shields.io/discord/783108952111579166.svg?color=7289da&logo=discord&style=flat-square)](https://discord.gg/yyPhbfma6f)

This api is designed to **retrieve data** TikTok. It **can not be used post or upload** content to TikTok on the behalf of a user. It has **no support for any user-authenticated routes**, if you can't access it while being logged out on their website you can't access it here.

## Sponsors

These sponsors have paid to be placed here or are my own affiliate links which I may earn a commission from, and beyond that I do not have any affiliation with them. The TikTokAPI package will always be free and open-source. If you wish to be a sponsor of this project check out my [GitHub sponsors page](https://github.com/sponsors/davidteather).

<div align="center">
    <a href="https://tikapi.io/?ref=davidteather" target="_blank">
        <img src="https://raw.githubusercontent.com/davidteather/TikTok-Api/main/imgs/tikapi.png" width="100" alt="TikApi">
        <div>
            <b>TikAPI</b> is a paid TikTok API service providing a full out-of-the-box solution, making life easier for developers — trusted by 500+ companies.
        </div>
    </a>
    <br>
    <a href="https://www.ensembledata.com/?utm_source=github&utm_medium=githubpage&utm_campaign=david_thea_github&utm_id=david_thea_github" target="_blank">
        <img src="https://raw.githubusercontent.com/davidteather/TikTok-Api/main/imgs/EnsembleData.png" width="100" alt="Ensemble Data">
        <b></b>
        <div>
         <b>EnsembleData</b> is the leading API provider for scraping Tiktok, Instagram, Youtube, and more. <br> Trusted by the major influencer marketing and social media listening platforms.
        </div>
    </a>
    <br>
    <a href="https://www.sadcaptcha.com?ref=davidteather" target="_blank">
        <img src="https://raw.githubusercontent.com/davidteather/TikTok-Api/main/imgs/tiktok_captcha_solver.png" width="100" alt="TikTok Captcha Solver">
        <b></b>
        <div>
         <b>TikTok Captcha Solver: </b> Bypass any TikTok captcha in just two lines of code.<br> Scale your TikTok automation and get unblocked with SadCaptcha.
        </div>
    </a>
    <br>
    <a href="https://www.webshare.io/?referral_code=3x5812idzzzp" target="_blank">
        <img src="https://raw.githubusercontent.com/davidteather/TikTok-Api/main/imgs/webshare.png" width="100" alt="TikTok Captcha Solver">
        <b></b>
        <div>
         <b>Cheap, Reliable Proxies: </b> Supercharge your web scraping with fast, reliable proxies. Try 10 free datacenter proxies today!
        </div>
    </a>
</div>

## Table of Contents

- [Documentation](#documentation)
- [Getting Started](#getting-started)
  - [How to Support The Project](#how-to-support-the-project)
  - [Installing](#installing)
  - [Common Issues](#common-issues)
- [Quick Start Guide](#quick-start-guide)
  - [Examples](https://github.com/davidteather/TikTok-Api/tree/main/examples)

[**Upgrading from V5 to V6**](#upgrading-from-v5-to-v6)

## Documentation

You can find the full documentation [here](https://davidteather.github.io/TikTok-Api)

## Getting Started

To get started using this API follow the instructions below.

**Note:** If you want to learn how to web scrape websites check my [free and open-source course for learning everything web scraping](https://github.com/davidteather/everything-web-scraping)

### How to Support The Project

- Star the repo 😎
- Consider [sponsoring](https://github.com/sponsors/davidteather) me on GitHub
- Send me an email or a [LinkedIn](https://www.linkedin.com/in/davidteather/) message telling me what you're using the API for, I really like hearing what people are using it for.
- Submit PRs for issues :)

### Installing

**Note:** Installation requires python3.9+

If you run into an issue please check the closed issues on the github, although feel free to re-open a new issue if you find an issue that's been closed for a few months. The codebase can and does run into similar issues as it has before, because TikTok changes things up.

```sh
pip install TikTokApi
python -m playwright install
```

If you would prefer a video walk through of setting up this package [YouTube video](https://www.youtube.com/watch?v=-uCt1x8kINQ) just for that. (is a version out of date, installation is the same though)

If you want a quick video to listen for [TikTok Live](https://www.youtube.com/watch?v=307ijmA3_lc) events in python.

#### Docker Installation

Clone this repository onto a local machine (or just the Dockerfile since it installs TikTokApi from pip) then run the following commands.

```sh
docker pull mcr.microsoft.com/playwright:focal
docker build . -t tiktokapi:latest
docker run -v TikTokApi --rm tiktokapi:latest python3 your_script.py
```

**Note** this assumes your script is named your_script.py and lives in the root of this directory.

### Common Issues

- **EmptyResponseException** - this means TikTok is blocking the request and detects you're a bot. This can be a problem with your setup or the library itself
  - you may need a proxy to successfuly scrape TikTok, I've made a [web scraping lesson](https://github.com/davidteather/everything-web-scraping/tree/main/002-proxies) explaining the differences of "tiers" of proxies, I've personally had success with [webshare's residential proxies](https://www.webshare.io/?referral_code=3x5812idzzzp) (affiliate link), but you might have success on their free data center IPs or a cheaper competitor.

- **Browser Has no Attribute** - make sure you ran `python3 -m playwright install`, if your error persists try the [playwright-python](https://github.com/microsoft/playwright-python) quickstart guide and diagnose issues from there.

- **API methods returning Coroutine** - many of the API's methods are async so make sure your program awaits them for proper functionality

## Quick Start Guide

Here's a quick bit of code to get the most recent trending videos on TikTok. There's more examples in the [examples](https://github.com/davidteather/TikTok-Api/tree/main/examples) directory.

**Note:** If you want to learn how to web scrape websites check my [free and open-source course for web scraping](https://github.com/davidteather/web-scraping-with-reverse-engineering)

```py
from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get("ms_token", None) # get your own ms_token from your cookies on tiktok.com

async def trending_videos():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        async for video in api.trending.videos(count=30):
            print(video)
            print(video.as_dict)

if __name__ == "__main__":
    asyncio.run(trending_videos())
```

To directly run the example scripts from the repository root, use the `-m` option on python.

```sh
python -m examples.trending_example
```

You can access the full data dictionary the object was created from with `.as_dict`. On a video this may look like
[this](https://gist.github.com/davidteather/7c30780bbc30772ba11ec9e0b909e99d). TikTok changes their structure from time to time so it's worth investigating the structure of the dictionary when you use this package.