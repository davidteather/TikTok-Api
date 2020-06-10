
# Unofficial TikTok API in Python

This is an unofficial api wrapper for TikTok.com in python. With this api you are able to call most trending and fetch specific user information.

 [![GitHub release (latest by date)](https://img.shields.io/github/v/release/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/releases) [![Build Status](https://travis-ci.com/davidteather/TikTok-Api.svg?branch=master)](https://travis-ci.com/davidteather/TikTok-Api) [![GitHub](https://img.shields.io/github/license/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/blob/master/LICENSE) [![PyPI - Downloads](https://img.shields.io/pypi/dm/TikTokApi)](https://pypi.org/project/TikTokApi/) [![Downloads](https://pepy.tech/badge/tiktokapi)](https://pypi.org/project/TikTokApi/)

If you want to use this API as a service visit the [RapidAPI](https://rapidapi.com/rapidapideveloper/api/tiktok2)


 Consider sponsoring me [here](https://github.com/sponsors/davidteather)

## Important Information
* If this API stops working for any reason open an issue.

## Getting Started

To get started using this api follow the instructions below.

### Installing

If you need help installing or run into some error, please open an issue. I will try to help out as much as I can.

```
pip install TikTokApi
pyppeteer-install
```

If you're running a virtual machine you need to install chromedriver for your machine globally. Download it [here](https://sites.google.com/a/chromium.org/chromedriver/) and add it to your path.

### Common Installation Issues

Please don't open an issue if you're experiencing one of these just comment if the provided solution do not work for you.

* [Browser closed unexpectedly](https://github.com/davidteather/TikTok-Api/issues/95)
* [BadStatusLine](https://github.com/davidteather/TikTok-Api/issues/88)

## Quick Start Guide

Here's a quick bit of code to get the most recent trending on TikTok. There's more example in the examples directory.


```
from TikTokApi import TikTokApi
api = TikTokApi()

results = 10

trending = api.trending(results)

for tiktok in trending:
    # Prints the text of the tiktok
    print(tiktok['desc'])

print(len(trending))
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
# Where count is how many result you want
# Verbose is optional, default=0. Set it to 1 to get more information
api.trending(self, count=30, referrer="https://www.tiktok.com/@ondymikula/video/6756762109670477061")
```

count - this is how many trending Tiktoks you want to be returned.

Trending returns an array of dictionaries. Example structure [here](https://www.tiktok.com/@ondymikula/video/6756762109670477061)

##### The get_Video_By_TikTok Method

```
api.get_Video_By_TikTok(data)
```

data - The tiktok dictionary returned from the API. Will return bytes.


##### The bySound Method

This method returns an array of tiktoks based on a sound id.
```
def bySound(self, id, count=30)
```

id - the sound's id (you can get this from other methods)


##### The getUserObject Method

This method returns a user object, primarily used for other methods within the package.
```
def getUserObject(self, username)
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
def getMusicObject(self, id)
```

id - the ID of the music.

##### The getHashtagObject Method

This method returns a hashtag (challenge) object, primarily used for other methods within the package.

```
def getHashtagObject(self, hashtag)
```

hashtag - the hashtag or challenge name

##### The byUsername Method

This method returns an array of tiktoks by a username

```
def byUsername(self, username, count=30)
```

##### The byHashtag Method

This method returns an array of TikToks by a given hashtag or challenge (without the #)

```
def byHashtag(self, hashtag, count=30)
```

hashtag - a given hashtag or challenge without the #

##### The discoverMusic Method

Returns trending music shown on the side at tiktok's trending page on desktop

```
def discoverMusic(self)
```

##### The discoverHashtags Method

Returns trending hashtags (challenges) shown on the side at tiktok's trending page on desktop

```
def discoverHashtags(self)
```

##### The getSuggestedUsersbyID Method

This method gets suggested users for a given userid.
```
getSuggestedUsersbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None)
```

##### The getSuggestedUsersbyIDCrawler Method

This method gets users across a variety of userids.
```
getSuggestedUsersbyIDCrawler(self, count=30, startingId='6745191554350760966')
```

##### The getSuggestedHashtagsbyID Method

This method gets related hashtags given a userid.
```
getSuggestedHashtagsbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None)
```

##### The getSuggestedHashtagsbyIDCrawler Method

This method crawls across multiple user's profile using the user crawler method to generate hashtags.
```
getSuggestedHashtagsbyIDCrawler(self, count=30, startingId='6745191554350760966')
```

##### The getSuggestedMusicbyID Method

This method gets suggested music given a userId
```
getSuggestedMusicbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None)
```

##### The getSuggestedMusicIDCrawler Method

This method crawls across multiple user's profile using the user crawler method to generate music objects.
```
getSuggestedMusicIDCrawler(self, count=30, startingId='6745191554350760966')
```

##### The get_Video_By_DownloadURL Method

```
api.get_Video_By_DownloadURL(url)
```

url - The download url that's found in the TikTok dictionary. TikTok['video']['downloadAddr']


##### The get_Video_By_Url Method

```
api.get_Video_By_Url(video_url, return_bytes=0)
```

video_url - The video you want to get url.

return_bytes - The default value is 0, when it is set to 1 the function instead returns the bytes from the video rather than just the direct url.

##### The get_Video_No_Watermark Method

```
api.get_Video_No_Watermark(video_url, return_bytes=0)
```

video_url - The video you want to get url.

return_bytes - The default value is 0, when it is set to 1 the function instead returns the bytes from the video rather than just the direct url.

## Built With

* [Python 3.7](https://www.python.org/) - The web framework used

## Authors

* **David Teather** - *Initial work* - [davidteather](https://github.com/davidteather)

See also the list of [contributors](https://github.com/davidteather/TikTok-Api/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
