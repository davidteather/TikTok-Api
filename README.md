
# Unofficial TikTok API in Python

This is an unofficial api wrapper for TikTok.com in python. With this api you are able to call most trending and fetch specific user information as well as much more.

 [![DOI](https://zenodo.org/badge/188710490.svg)](https://zenodo.org/badge/latestdoi/188710490) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&style=flat-square)](https://www.linkedin.com/in/davidteather/) [![Sponsor Me](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub)](https://github.com/sponsors/davidteather)  [![GitHub release (latest by date)](https://img.shields.io/github/v/release/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/releases) [![Build Status](https://img.shields.io/github/workflow/status/davidteather/tiktok-api/TikTokApi%20CI/master)](https://github.com/davidteather/TikTok-Api/actions/workflows/package-test.yml) [![GitHub](https://img.shields.io/github/license/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/blob/master/LICENSE) [![Downloads](https://pepy.tech/badge/tiktokapi)](https://pypi.org/project/TikTokApi/) ![](https://visitor-badge.laobi.icu/badge?page_id=davidteather.TikTok-Api) [![Support Server](https://img.shields.io/discord/783108952111579166.svg?color=7289da&logo=discord&style=flat-square)](https://discord.gg/yyPhbfma6f)

## Sponsors
These sponsors have paid to be placed here and beyond that I do not have any affiliation with them, the TikTokAPI package will always be free and open-source. If you wish to be a sponsor of this project check out my [GitHub sponsors page](https://github.com/sponsors/davidteather).

<div align="center">
    <p>
    <a href="https://tikapi.io/?ref=davidteather" target="_blank">
			<div>
				<img src="https://raw.githubusercontent.com/davidteather/TikTok-Api/master/imgs/logo128.png" width="100" alt="TikApi">
			</div>
			<b></b>
			<div>
				TikApi is a paid TikTok API service providing an full out-of-the-box solution for developers, trusted by 100+ companies.
			</div>
		</a>
    </p>
</div>

<br>

<div align="center">
    <p>
    <a href="https://trendpop.social/?ref=github-davidteather-tiktokapi" target="_blank">
			<div>
				<img src="https://raw.githubusercontent.com/davidteather/TikTok-Api/master/imgs/trendpop.png" width="100" alt="Trendpop">
			</div>
			<div>
				Trendpop builds software to help creators and businesses go viral on social video platforms.
			</div>
            <div>
                <sub>
                    Excited about building in this space?
                    <a href="https://trendpop.social/careers?ref=github-davidteather-tiktokapi">
                        <sub>We're hiring engineers across all roles</sub>
                    </a>
                    <a href="https://trendpop.social/careers?ref=github-davidteather-tiktokapi" target="_blank">
                    <sub>- shoot us a message at </sub>
                    </a>
                    <a href="mailto:founders@trendpop.social" target="_blank">
                    <sub><code>founders@trendpop.social</code></sub>
                    </a>
                </sub>
            </div>
		</a>
    </p>
</div>

<br>

<div align="center">
    <p>
    <a href="https://influencerhunters.com/docs.html?utm_source=github&utm_medium=githubpage&utm_campaign=david_thea_github&utm_id=david_t" target="_blank">
			<div>
				<img src="https://raw.githubusercontent.com/andrearama/TikTok-Api/master/imgs/IH_LOGO.png" width="100" alt="IH_logo">
			</div>
			<b></b>
			<div>
				TikTok data through APIs, providing 10+ Million posts / day to the largest Marketing and Social listening platforms.
			</div>
		</a>
    </p>
</div>

## Table of Contents
- [Documentation](#documentation)
- [Getting Started](#getting-started)
    - [How to Support The Project](#how-to-support-the-project)
    - [Installing](#installing)
    - [Common Issues](#common-issues)
- [Quick Start Guide](#quick-start-guide)
    - [Examples](https://github.com/davidteather/TikTok-Api/tree/master/examples)

[**Upgrading from V4 to V5**](#upgrading-from-v4-to-v5)

## Documentation

You can find the full documentation [here](https://davidteather.github.io/TikTok-Api/docs/TikTokApi.html), the [TikTokApi Class](https://davidteather.github.io/TikTok-Api/docs/TikTokApi/tiktok.html) is where you'll probably spend most of your time.
## Getting Started

To get started using this api follow the instructions below.

**Note:** If you want to learn how to web scrape websites check my [free and open-source course for web scraping](https://github.com/davidteather/web-scraping-with-reverse-engineering)

### How to Support The Project
* Star the repo 😎
* Consider [sponsoring](https://github.com/sponsors/davidteather) me on GitHub
* Send me an email or a [LinkedIn](https://www.linkedin.com/in/davidteather/) message telling me what you're using the API for, I really like hearing what people are using it for.
* Submit PRs for issues :)

### Installing

If you run into an issue please check the closed issues on the github, although feel free to re-open a new issue if you find an issue that's been closed for a few months. The codebase can and does run into similar issues as it has before, because TikTok changes things up.

```sh
pip install TikTokApi
python -m playwright install
```
If you would prefer a video walk through of setting up this package [YouTube video](https://www.youtube.com/watch?v=-uCt1x8kINQ) just for that.

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

Please don't open an issue if you're experiencing one of these just comment if the provided solution do not work for you.

* **Browser Has no Attribute** - make sure you ran `python3 -m playwright install`, if your error persists try the [playwright-python](https://github.com/microsoft/playwright-python) quickstart guide and diagnose issues from there.

## Quick Start Guide

Here's a quick bit of code to get the most recent trending videos on TikTok. There's more examples in the [examples](https://github.com/davidteather/TikTok-Api/tree/master/examples) directory.

**Note:** If you want to learn how to web scrape websites check my [free and open-source course for web scraping](https://github.com/davidteather/web-scraping-with-reverse-engineering)

```py
from TikTokApi import TikTokApi

# Watch https://www.youtube.com/watch?v=-uCt1x8kINQ for a brief setup tutorial
with TikTokApi() as api:
    for trending_video in api.trending.videos(count=50):
        # Prints the author's username of the trending video.
        print(trending_video.author.username)
```

**Note**: Jupyter (ipynb) only works on linux, see [microsoft/playwright-python #178](https://github.com/microsoft/playwright-python/issues/178)

To run the example scripts from the repository root, make sure you use the `-m` option on python.
```sh
python -m examples.get_trending
```

You can access the dictionary type of an object using `.as_dict`. On a video this may look like
[this](https://gist.github.com/davidteather/7c30780bbc30772ba11ec9e0b909e99d), although TikTok changes their structure from time to time so it's worth investigating the structure of the dictionary when you use this package.

## Upgrading from V4 to V5

All changes will be noted on [#803](https://github.com/davidteather/TikTok-Api/pull/803) if you want more information.

### Motivation

This package has been difficult to maintain due to it's structure, difficult to work with since the user of the package must write parsing methods to extract information from dictionaries, more memory intensive than it needs to be (although this can be further improved), and in general just difficult to work with for new users. 

As a result, I've decided to at least attempt to remedy some of these issues, the biggest changes are that 
1. The package has shifted to using classes for different TikTok objects resulting in an easier, higher-level programming experience.
2. All methods that used to return a list of objects have been switched to using iterators, to hopefully decrease memory utilization for most users.


### Upgrading Examples


#### Accessing Dictionary on Objects (similar to V4)

You'll probably need to use this beyond just for legacy support, since not all attributes are parsed out and attached
to the different objects.

You may want to use this as a workaround for legacy applications while you upgrade the rest of the app. I'd suggest that you do eventually upgrade to using the higher-level approach fully.
```py
user = api.user(username='therock')
user.as_dict # -> dict of the user_object
for video in user.videos():
    video.as_dict # -> dict of TikTok's video object as found when requesting the videos endpoint
```

Here's a few more examples that help illustrate the differences in the flow of the usage of the package with V5.

```py
# V4
api = TikTokApi.get_instance()
trending_videos = api.by_trending()

#V5.1
with TikTokApi() as api: # .get_instance no longer exists
    for trending_video in api.trending.videos():
        # do something
```

Where in V4 you had to extract information yourself, the package now handles that for you. So it's much easier to do chained related function calls.
```py
# V4
trending_videos = api.by_trending()
for video in trending_videos:
    # The dictionary responses are also different depending on what endpoint you got them from
    # So, it's usually more painful than this to deal with
    trending_user = api.get_user(id=video['author']['id'], secUid=video['author']['secUid'])


# V5
# This is more complicated than above, but it illustrates the simplified approach
for trending_video in api.trending.videos():
    user_stats = trending_video.author.info_full['stats']
    if user_stats['followerCount'] >= 10000:
        # maybe save the user in a database
```
