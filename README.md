
# Unoffical TikTok API in Python

This is an unoffical api wrapper for tiktok.com in python. With this api you are able to call most trending and fetch specific user information.

 [![GitHub release (latest by date)](https://img.shields.io/github/v/release/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/releases) [![Build Status](https://travis-ci.com/davidteather/TikTok-Api.svg?branch=master)](https://travis-ci.com/davidteather/TikTok-Api) [![GitHub](https://img.shields.io/github/license/davidteather/TikTok-Api)](https://github.com/davidteather/TikTok-Api/blob/master/LICENSE) [![PyPI - Downloads](https://img.shields.io/pypi/dm/TikTokApi)](https://pypi.org/project/TikTokApi/)

## Important Information
* If this API stops working for any reason open an issue.
* Feel free to mention @davidteather in an issue you open, because I might not see it otherwise.

## Getting Started

To get started using this api follow the instructions below.

It is quite a long installation process just for a TikTok api, the first release can be found [here](https://github.com/davidteather/TikTok-Api/releases/edit/v1.0) and is not as suitable for long term projects, however it may be easier for a day of scraping TikTok, as the installation is much easier.

Despite this, I **still recommend** you follow this process and use the latest version.

### Installing

If you need help installing or run into some error, please open an issue. I will try to help out as much as I can.

Tested with python 3.7.3

```
pip install TikTokApi
```

Or install directly from this GitHub repo.

* You do need to have **java installed**
* Download browsermob-proxy [here](https://bmp.lightbody.net/)
* You must add **browsermob-proxy/bin** to your environment path.
* **Firefox** must be installed.
* You must download the latest **geckodriver** from [mozilla](https://github.com/mozilla/geckodriver/releases), and include the .exe in your path.

## Quick Start Guide

Here's a quick bit of code to get the most recent trending on TikTok

```
from tiktok import TikTokapi

api = TikTokapi(path_to_browsermob_directory)
# path_to_browsermob_directory - String - should be the path from the directory you are running from the code to the extracted zip file of [browsermob-proxy](https://bmp.lightbody.net/)
# Will Get the 10 most recent trending on the tiktok trending page
api.trending(10)
```

## Detailed Documentation

##### The TikTok class

```
# Variable set like
api = TikTokapi(path_to_browsermob_directory, headless=False)
```
path_to_browsermob_directory - String - should be the path from the directory you are running from the code to the extracted zip file of [browsermob-proxy](https://bmp.lightbody.net/)
headless - True/False - True means it will run a headless firefox browser, could be detected by TikTok, however it is more convienent. Default = False.


##### The Trending Method

```
# Where count is how many result you want
# Verbose is optional, default=0. Set it to 1 to get more information
api.trending(count, verbose)
```

Trending returns an array of json objects. Example structure [here](https://gist.github.com/davidteather/0be2e495e2de54098e8f2a9594581d27)

JSON object tree [here](https://gist.github.com/davidteather/bc4baef0edb621dd322c8ad128a31ac1)

##### The userPosts Method

```
api.userPosts(userid, secUid, count, verbose)
```

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

##### The get_trending_hashtags Method

```
api.get_trending_hashtags()
```

This returns the 4 displayed trending hashtags in an array, this does change on every new instance of the api as it changes on page refreshes. 

## Built With

* [Python 3.7](https://www.python.org/) - The web framework used

## Authors

* **David Teather** - *Initial work* - [davidteather](https://github.com/davidteather)

See also the list of [contributors](https://github.com/davidteather/TikTok-Api/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
