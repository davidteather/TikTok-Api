
# Unofficial TikTok API in Python

This is an unofficial api wrapper for TikTok.com in python. With this api you are able to call most trending and fetch specific user information as well as much more.

 [![GitHub release (latest by date)](https://img.shields.io/github/v/release/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/releases) [![Build Status](https://travis-ci.com/davidteather/TikTok-Api.svg?branch=master)](https://travis-ci.com/davidteather/TikTok-Api) [![GitHub](https://img.shields.io/github/license/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/blob/master/LICENSE) [![Downloads](https://pepy.tech/badge/tiktokapi)](https://pypi.org/project/TikTokApi/) ![](https://visitor-badge.laobi.icu/badge?page_id=davidteather.TikTok-Api)

If you want to use this API as a service visit the [RapidAPI](https://rapidapi.com/rapidapideveloper/api/tiktok2)


Consider sponsoring me [here](https://github.com/sponsors/davidteather)

## Table of Contents
- [Getting Started](#getting-started)
    - [Installing](#installing)
    - [Common Issues](#common-issues)
- [Quick Start Guide](#quick-start-guide)
    - [Examples](https://github.com/davidteather/TikTok-Api/tree/master/examples)
- [Detailed Documentation](#detailed-documentation)
    - [Common Parameters](#common-parameters)
    - [Methods](#methods)
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
- [Built With](#built-with)
- [Authors](#authors)
- [License](#license)

## Getting Started

To get started using this api follow the instructions below.

### Installing

If you run into an issue please check the closed issues on the github. You're most likely not the first person to experience this issue. If nothing works feel free to open an issue.

```
pip install TikTokApi
```

The script should download pypppeteer by default, but if it doesn't run the following command.
```
pyppeteer-install
```

If you run into any issue try the fix below before posting an issue.


**If you still run into issues you may need to install chromedriver for your machine globally. Download it [here](https://sites.google.com/a/chromium.org/chromedriver/) and add it to your path.**

### Common Issues

Please don't open an issue if you're experiencing one of these just comment if the provided solution do not work for you.

* [Browser closed unexpectedly](https://github.com/davidteather/TikTok-Api/issues/95)
* [BadStatusLine](https://github.com/davidteather/TikTok-Api/issues/88)

## Quick Start Guide

Here's a quick bit of code to get the most recent trending on TikTok. There's more examples in the examples directory.

```
from TikTokApi import TikTokApi
api = TikTokApi()

results = 10

trending = api.trending(count=results)

for tiktok in trending:
    # Prints the text of the tiktok
    print(tiktok['desc'])

print(len(trending))
```

To run the example scripts from the repository root, make sure you use the
module form of python the interpreter

```sh
python -m examples.getTrending
```

[Here's](https://gist.github.com/davidteather/7c30780bbc30772ba11ec9e0b909e99d) an example of what a tiktok dictionary looks like.

## Detailed Documentation

**Note**: This documentation is called detailed, which it is, but it may be out of date. And if you see something wrong or want to improve the documentation feel free to open a PR with the fixes.

#### Common Parameters

* username - the userame of a user you want to find
* secUid - the secUid of the user (you can find in the responses)
* userId / id - The id of the user
* proxy - the proxy address of your proxy
* language - the 2 letter code for your language (this is included in the requests by default to TikTok, but it doesn't seem to do much for me at least)

##### The TikTok class

```
TikTokApi(self, debug=False)
```

debug - Enable this if you need some more output.

##### The trending Method

```
api.trending(self, count=30, referrer="https://www.tiktok.com/@ondymikula/video/6756762109670477061", language='en', proxy=None)
```

count - this is how many trending Tiktoks you want to be returned.

Trending returns an array of dictionaries. Example structure [here](https://www.tiktok.com/@ondymikula/video/6756762109670477061)

##### The get_Video_By_TikTok Method

```
api.get_Video_By_TikTok(data, language='en', proxy=None)
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
api.get_Video_By_DownloadURL(url, language='en', proxy=None)
```

url - The download url that's found in the TikTok dictionary. TikTok['video']['downloadAddr']


##### The get_Video_By_Url Method

```
api.get_Video_By_Url(video_url, return_bytes=0)
```

video_url - The video you want to get url.

return_bytes - The default value is 0, when it is set to 1 the function instead returns the bytes from the video rather than just the direct url.

##### The get_Video_No_Watermark_Faster Method

```
api.get_Video_No_Watermark(video_url, return_bytes=0, language='en', proxy=None)
```

video_url - The video you want to get url.

return_bytes - The default value is 0, when it is set to 1 the function instead returns the bytes from the video rather than just the direct url.

If you request without bytes you will need to make a call to the URL it responds yourself to get bytes.
```
url = api.get_Video_No_Watermark_ID('6829267836783971589', return_bytes=0)

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
api.get_Video_No_Watermark_ID(self, video_id, return_bytes=1, proxy=None)
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
api.get_Video_No_Watermark(self, video_url, return_bytes=0, proxy=None)
```

This endpoint returns a url that is able to be opened in any browser, but sacrifices speed for this convenience. Any old request library can return the bytes if you decide to return a url.

video_url - the url of the video you wish to download

return_bytes - if you want to return bytes or a url

##### The getUserPager method
```
api.getUserPager(username, page_size=30, before=0, after=0)
```
This endpoint returns a generator, which emits pages of tiktok records posted by the user specified by `username`.
The size of the pages can be specified with `page_size`.  The generator will request the next `page` of results
lazily, and terminate once the TikTok api indicates that the feed has been exhausted.

`before` and `after` are cursor parameters that accept millisecond-precision UNIX timestamps. Note that the generator
does use these values internally to manage paging, but if you pass them in here that will only set their 'starting
points.  For `after`, that means setting a hard limit on how far back in the user's feed to go, bur `before` sets the
starting point for pagination.  If they are not passed (or 0 is passed for them), then the pager will be able to
traverse the user's entire feed.

One more note: The pages of results are often one or two records short of the full `page_size` specified, even if
there are more results.  This doesn't mean that tiktoks are being missed, just that TikTok didn't deign to fill the
page completely.

username - TikTok username for the user from which to request tiktoks

page_size - integer specifying the maximum number of tiktoks to return in a page (default 30)

after - millisecond-precision UNIX timestamp. only tiktoks posted after that time will be retrieved. (default 0)

before - millisecond-precision UNIX timestamp.  only tiktoks posted before that time will be retrieved. (default infinity)

##### The getHashtagPager method
```
api.getHashtagPager(hashtag, page_size=30)
```
This endpoint returns a generator, which emits pages of tiktok records posted under a given hashtag. The size
of the pages can be specified with `page_size`.  The generator will request the next `page` of results lazily, and
terminate once the TikTok api indicates that the feed has been exhausted.

One more note: The pages of results are often one or two records short of the full `page_size` specified, even if
there are more results.  This doesn't mean that tiktoks are being missed, just that TikTok didn't deign to fill the
page completely.

hashtag - string representation of the hashtag in question (without the '#' prefix)

page_size - integer specifying the maximum number of tiktoks to return in a page (default 30)


## Built With

* [Python 3.7](https://www.python.org/) - The web framework used

## Authors

* **David Teather** - *Initial work* - [davidteather](https://github.com/davidteather)

See also the list of [contributors](https://github.com/davidteather/TikTok-Api/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
