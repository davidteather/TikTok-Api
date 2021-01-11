
# Unofficial TikTok API in Python

This is an unofficial api wrapper for TikTok.com in python. With this api you are able to call most trending and fetch specific user information as well as much more.

 [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&style=flat-square)](https://www.linkedin.com/in/davidteather/) [![Sponsor Me](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub)](https://github.com/sponsors/davidteather)  [![GitHub release (latest by date)](https://img.shields.io/github/v/release/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/releases) [![Build Status](https://travis-ci.com/davidteather/TikTok-Api.svg?branch=master)](https://travis-ci.com/davidteather/TikTok-Api) [![GitHub](https://img.shields.io/github/license/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/blob/master/LICENSE) [![Downloads](https://pepy.tech/badge/tiktokapi)](https://pypi.org/project/TikTokApi/) ![](https://visitor-badge.laobi.icu/badge?page_id=davidteather.TikTok-Api) [![Support Server](https://img.shields.io/discord/783108952111579166.svg?color=7289da&logo=discord&style=flat-square)](https://discord.gg/yyPhbfma6f)

## Table of Contents
- [Getting Started](#getting-started)
    - [Installing](#installing)
    - [Common Issues](#common-issues)
- [Quick Start Guide](#quick-start-guide)
    - [Examples](https://github.com/davidteather/TikTok-Api/tree/master/examples)
- [Detailed Documentation](#detailed-documentation)
    - [Common Parameters](#common-parameters)
    - [TikTok Class](#the-tiktok-class)
        - [get_Video_By_TikTok](#the-get_video_by_tiktok-method)
        - [bySound](#the-bysound-method)
        - [getUserObject](#the-getuserobject-method)
        - [getTikTokById](#the-gettiktokbyid-method)
        - [getTikTokByUrl](#the-gettiktokbyurl-method)
        - [getUser](#the-getuser-method)
        - [getMusicObject](#the-getmusicobject-method)
        - [getHashtagObject](#the-gethashtagobject-method)
        - [byUsername](#the-by-username-method)
        - [byHashtag](#the-byhashtag-method)
        - [discoverMusic](#the-dicovermusic-method)
        - [discoverHashtags](#the-discoverhashtags-method)
        - [getSuggestedUsersbyID](#the-getsuggestedusersbyid-method)
        - [getSuggestedUsersbyIDCrawler](#the-getssuggestedusersbyidcrawler-method)
        - [getSuggestedHashtagsbyID](#the-getsuggestedhashtagsbyid-method)
        - [getSuggestedHashtagsbyIDCrawler](#the-getsuggestedhashtagsbyidcrawler-method)
        - [getSuggestedMusicbyID](#the-getsuggestedmusicbyid-method)
        - [getSuggestedMusicIDCrawler](#the-getsuggestedmusicidcrawler-method)
        - [get_Video_By_DownloadURL](#the-get_video_by_downloadurl-method)
        - [get_Video_By_Url](#the-get_video_by_url-method)
        - [get_Video_No_Watermark](#the-get_video_no_watermark-method)
        - [search_for_users](#the-search_for_users-method)
        - [search_for_music](#the-search_for_music-method)
        - [search_for_hashtags](#the-search_for_hashtags-method)
        - [discover_type](#the-discover_type-method)
        - [userLiked](#the-userliked-method)
        - [userLikedbyUsername](#the-userlikedbyusername-method)
    - [TikTokUser Class](#the-tiktokuser-class)
        - [get_insights](#the-get_insights-method)
- [Built With](#built-with)
- [Authors](#authors)
- [License](#license)

## Getting Started

To get started using this api follow the instructions below.

### Installing

If you run into an issue please check the closed issues on the github. You're most likely not the first person to experience this issue. If nothing works feel free to open an issue.

```
pip install TikTokApi
python -m playwright install
```
If you would prefer a video walk through of setting up this package I created a [YouTube video](https://www.youtube.com/watch?v=zwLmLfVI-VQ) just for that.



If you're on MacOS you may need to install [XCode Developer Tools](https://webkit.org/build-tools/)

#### Docker Installation

Clone this repository onto a local machine then run the following commands.

```
docker build . -t tiktokapi:latest
docker run -v TikTokApi --rm tiktokapi:latest python3 your_script.py
```

**Note** this assumes your script is named your_script.py and lives in the root of this directory.

### Common Issues

Please don't open an issue if you're experiencing one of these just comment if the provided solution do not work for you.

* [Browser object has no attribute verifyFp](https://github.com/davidteather/TikTok-Api/issues/237) There's so many issues by this error please search (open and closed) issues before posting
* [Browser closed unexpectedly](https://github.com/davidteather/TikTok-Api/issues/95)
* [BadStatusLine](https://github.com/davidteather/TikTok-Api/issues/88)

## Quick Start Guide

Here's a quick bit of code to get the most recent trending on TikTok. There's more examples in the examples directory.

```
from TikTokApi import TikTokApi
api = TikTokApi.get_instance()
# If playwright doesn't work for you try to use selenium
# api = TikTokApi.get_instance(use_selenium=True)

results = 10

# Since TikTok changed their API you need to use the custom_verifyFp option. 
# In your web browser you will need to go to TikTok, Log in and get the s_v_web_id value.
trending = api.trending(count=results, custom_verifyFp="")

for tiktok in trending:
    # Prints the id of the tiktok
    print(tiktok['id'])

print(len(trending))
```

To run the example scripts from the repository root, make sure you use the
module form of python the interpreter

```
python -m examples.getTrending
```

[Here's](https://gist.github.com/davidteather/7c30780bbc30772ba11ec9e0b909e99d) an example of what a tiktok dictionary looks like.

## Detailed Documentation

**Note**: This documentation is called detailed, which it is, but it may be out of date. And if you see something wrong or want to improve the documentation feel free to open a PR with the fixes.

#### Common Parameters

* username - the username of a user you want to find
* secUid - the secUid of the user (you can find in the responses)
* userId / id - The id of the user
* proxy - the proxy address of your proxy
* language - the 2 letter code for your language (this is included in the requests by default to TikTok, but it doesn't seem to do much for me at least)
* language - Ex: en (doesn't seem to change data)
* region - Ex: US (doesn't seem to change data)

#### The TikTok class

```
TikTokApi(self, debug=False, request_delay=None, executablePath=None)
```

debug - Enable this if you need some more output.

request_delay - The time to wait in seconds before sending a request.

executablePath - The path to your chromedriver if you don't want global install of chromedriver.

##### The trending Method

```
api.trending(self, count=30, referrer="https://www.tiktok.com/@ondymikula/video/6756762109670477061", language='en', proxy=None, , custom_verifyFp="")
```

count - this is how many trending Tiktoks you want to be returned.

Trending returns an array of dictionaries. Example structure [here](https://www.tiktok.com/@ondymikula/video/6756762109670477061)

##### The get_Video_By_TikTok Method

```
api.get_Video_By_TikTok(data, language='en', proxy=None, , custom_verifyFp="")
```

data - The tiktok dictionary returned from the API. Will return bytes.


##### The bySound Method

This method returns an array of tiktoks based on a sound id.
```
def bySound(self, id, count=30, language='en', proxy=None)
```

id - the sound's id (you can get this from other methods)


##### The getUserObject Method

This method returns a user object, primarily used for other methods within the package.
```
def getUserObject(self, username, language='en', proxy=None)
```

##### The getTikTokById Method

This object returns a TikTok object when given the TikTok ID.
```
def getTikTokById(self, id, language='en', proxy=None)
```

##### The getTikTokByUrl Method

This does the same as the getTikTokById method, but it extracts the id out of the url.
```
def getTikTokByUrl(self, url, language='en', proxy=None)
```

##### The getUser Method

This method returns a user object, including all profile data about the user.
```
def getUser(self, username, language='en', proxy=None)
```

username - the unique username of the person you want to get an object for.

##### The getMusicObject Method

This method returns a music object, primarily used for other methods within the package.

```
def getMusicObject(self, id, language='en', proxy=None)
```

id - the ID of the music.

##### The getHashtagObject Method

This method returns a hashtag (challenge) object, primarily used for other methods within the package.

```
def getHashtagObject(self, hashtag, language='en', proxy=None)
```

hashtag - the hashtag or challenge name

##### The byUsername Method

This method returns an array of tiktoks by a username

```
def byUsername(self, username, count=30, language='en', proxy=None)
```

##### The byHashtag Method

This method returns an array of TikToks by a given hashtag or challenge (without the #)

```
def byHashtag(self, hashtag, count=30, language='en', proxy=None)
```

hashtag - a given hashtag or challenge without the #

##### The discoverMusic Method

Returns trending music shown on the side at tiktok's trending page on desktop

```
def discoverMusic(self, language='en', proxy=None)
```

##### The discoverHashtags Method

Returns trending hashtags (challenges) shown on the side at tiktok's trending page on desktop

```
def discoverHashtags(self, language='en', proxy=None)
```

##### The userLiked Method

Returns a list of a given user's liked TikToks. Returns a length of 0 if private list.
```
userLiked(self, userID, secUID, count=30, language='en', region='US', proxy=None)
```

### The userLikedbyUsername Method

Returns a list of a given user's liked TikToks. Returns a length of 0 if private list.
```
userLikedbyUsername(self, username, count=30, proxy=None, language='en', region='US')
```

##### The getSuggestedUsersbyID Method

This method gets suggested users for a given userid.
```
getSuggestedUsersbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None)
```

##### The getSuggestedUsersbyIDCrawler Method

This method gets users across a variety of userids.
```
getSuggestedUsersbyIDCrawler(self, count=30, startingId='6745191554350760966', language='en', proxy=None)
```

##### The getSuggestedHashtagsbyID Method

This method gets related hashtags given a userid.
```
getSuggestedHashtagsbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None)
```

##### The getSuggestedHashtagsbyIDCrawler Method

This method crawls across multiple user's profile using the user crawler method to generate hashtags.
```
getSuggestedHashtagsbyIDCrawler(self, count=30, startingId='6745191554350760966', language='en', proxy=None)
```

##### The getSuggestedMusicbyID Method

This method gets suggested music given a userId
```
getSuggestedMusicbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None)
```

##### The getSuggestedMusicIDCrawler Method

This method crawls across multiple user's profile using the user crawler method to generate music objects.
```
getSuggestedMusicIDCrawler(self, count=30, startingId='6745191554350760966', language='en', proxy=None)
```

##### The get_Video_By_DownloadURL Method

```
api.get_Video_By_DownloadURL(url, language='en', proxy=None, custom_verifyFp="")
```

url - The download url that's found in the TikTok dictionary. TikTok['video']['downloadAddr']


##### The get_Video_By_Url Method

```
api.get_Video_By_Url(video_url, return_bytes=0, custom_verifyFp="")
```

video_url - The video you want to get url.

return_bytes - The default value is 0, when it is set to 1 the function instead returns the bytes from the video rather than just the direct url.

##### The get_Video_No_Watermark_Faster Method

```
api.get_Video_No_Watermark(video_url, return_bytes=0, language='en', proxy=None, custom_verifyFp="")
```

video_url - The video you want to get url.

return_bytes - The default value is 0, when it is set to 1 the function instead returns the bytes from the video rather than just the direct url.

If you request without bytes you will need to make a call to the URL it responds yourself to get bytes.
```
url = api.get_Video_No_Watermark_ID('6829267836783971589', return_bytes=0, custom_verifyFp="")

import requests
video_bytes = requests.get(url, headers={"User-Agent": "okhttp"}).content
```

##### The search_for_users Method

```
def search_for_users(self, search_term, count=28, **kwargs)
```

Searches for users given a search term.

##### The search_for_music Method

```
def search_for_music(self, search_term, count=28, **kwargs)
```

Searches for music given a search term

##### The search_for_hashtags Method

```
def search_for_hashtags(self, search_term, count=28, **kwargs)
```

Searches for hashtags given a search term.

##### The discover_type Method

```
discover_type(self, search_term, prefix, count=28, **kwargs)
```

You can use this method if you really want, but just use the 3 above it.

##### The get_Video_No_Watermark_ID Method

```
api.get_Video_No_Watermark_ID(self, video_id, return_bytes=1, proxy=None, custom_verifyFp="")
```

video_id - The video id you want to get.

return_bytes - The default value is 0, when it is set to 1 the function instead returns the bytes from the video rather than just the direct url.


If you request without bytes you will need to make a call to the URL it responds yourself to get bytes.
```
url = api.get_Video_No_Watermark_ID('6829267836783971589', return_bytes=0)

import requests
video_bytes = requests.get(url, headers={"User-Agent": "okhttp"}).content
```

##### The get_Video_No_Watermark Method
```
api.get_Video_No_Watermark(self, video_url, return_bytes=0, proxy=None, custom_verifyFp="")
```

This endpoint returns a url that is able to be opened in any browser, but sacrifices speed for this convenience. Any old request library can return the bytes if you decide to return a url.

video_url - the url of the video you wish to download

return_bytes - if you want to return bytes or a url

#### The TikTokUser class

```
user = TikTokUser(self, user_cookie, debug=False)
```
user_cookie - The cookie of the logged in user. To get this string log into the desktop site of TikTok and go to the javascript console and type in document.cookie and copy that string and pass it in here.


debug - Enable this if you need some more output.


Will be denoted by user for the methods below

##### The get_Video_No_Watermark Method
```
user.get_insights(videoID, username=None)
```

This endpoint returns a the insights/analytics for a specific TikTok video.

videoID - The id of the TikTok

username - You don't need to provide this, but it's possible TikTok compares the refer header in the future so it's more robust to do this.


## Built With

* [Python 3.7](https://www.python.org/) - The web framework used

## Authors

* **David Teather** - *Initial work* - [davidteather](https://github.com/davidteather)

See also the list of [contributors](https://github.com/davidteather/TikTok-Api/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
