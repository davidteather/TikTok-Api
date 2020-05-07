
# Unoffical TikTok API in Python

This is an unoffical api wrapper for tiktok.com in python. With this api you are able to call most trending and fetch specific user information.

 [![GitHub release (latest by date)](https://img.shields.io/github/v/release/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/releases) [![Build Status](https://travis-ci.com/davidteather/TikTok-Api.svg?branch=master)](https://travis-ci.com/davidteather/TikTok-Api) [![GitHub](https://img.shields.io/github/license/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/blob/master/LICENSE) [![PyPI - Downloads](https://img.shields.io/pypi/dm/TikTokApi)](https://pypi.org/project/TikTokApi/) [![Downloads](https://pepy.tech/badge/tiktokapi)](https://pypi.org/project/TikTokApi/)

## Important Information
* If this API stops working for any reason open an issue.

## Getting Started

To get started using this api follow the instructions below.

### Installing

If you need help installing or run into some error, please open an issue. I will try to help out as much as I can.

```
pip install TikTokApi
```

## Quick Start Guide

Here's a quick bit of code to get the most recent trending on TikTok. There's more example in the examples directory.

[Here's](https://gist.github.com/davidteather/7c30780bbc30772ba11ec9e0b909e99d) an example of what a tiktok dictionary looks like.

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

## Detailed Documentation

##### The TikTok class

```
TikTokApi(self, debug=False)
```

debug - Enable this if you need some more output.


##### The Trending Method

```
# Where count is how many result you want
# Verbose is optional, default=0. Set it to 1 to get more information
api.trending(self, count=30, referrer="https://www.tiktok.com/@ondymikula/video/6756762109670477061")
```

count - this is how many trending Tiktoks you want to be returned.

Trending returns an array of dictionaries. Example structure [here](https://www.tiktok.com/@ondymikula/video/6756762109670477061)


##### The userPosts Method

```
api.userPosts(username="", id="", secUid="", count, verbose)
```

You can either define username OR BOTH id and secUid. Defining secUid and id is much faster than defining it by username, but it's still an option.

username - the username of the tiktok user without the @

userid - The id of the user, can be found in the TikTok json response titled "userId"

secUid - Also found in the TikTok json response the key anme is "secUid"


**Note:** Currently limited to 30 because of some issues with getting past 30. It will raise an exception if you try for higher.


Trending returns an array of json objects. Example structure [here](https://gist.github.com/davidteather/a5c1e54de353353f77a78139d2e5a9f9)

It has the same JSON object tree as trending. It's [here](https://gist.github.com/davidteather/bc4baef0edb621dd322c8ad128a31ac1) anyways.

##### The search_by_hashtag Method

```
api.search_by_hashtag(hashtag, count=10)
```

hashtag - A string of the hashtag without the # mark. Ex: hashtag = "funny"


count - The number of results you want


**Note:** Currently limited to 30 because of some issues with getting past 30. It will raise an exception if you try for higher.


Since this isn't an offical TikTok API the TikTok servers don't know what to do with my bad solutions, this takes a bit longer as it needs to find the hashtagID and stuff.


Search by hashtag returns an array of json objects. Example structure [here](https://gist.github.com/davidteather/a5c1e54de353353f77a78139d2e5a9f9)


It has the same JSON object tree as trending. It's [here](https://gist.github.com/davidteather/bc4baef0edb621dd322c8ad128a31ac1) anyways.

##### The get_Video_By_Url Method

```
api.get_Video_By_Url(video_url, return_bytes=0)
```

video_url - The video you want to get url.

return_bytes - The default value is 0, when it is set to 1 the function instead returns the bytes from the video rather than just the direct url.

##### The get_Related_Videos Method

```
api.get_Related_Videos(video_url)
```

This method returns the suggested trending videos titled "trends for you" on desktop. 

video_url - the video URL that you want to see related videos for 

##### The search_by_sound Method

```
api.search_by_sound(soundLink, count=10, verbose=0)
```

This method returns the trending videos under a specific sound or music link.

soundLink - Either the original sound link or the music link for a specific song.

count - Limited to 30 due to weird restrictions on the api.

verbose - 0/1 for debugging.

## Built With

* [Python 3.7](https://www.python.org/) - The web framework used

## Authors

* **David Teather** - *Initial work* - [davidteather](https://github.com/davidteather)

See also the list of [contributors](https://github.com/davidteather/TikTok-Api/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
