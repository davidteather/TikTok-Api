# Unoffical TikTok API in Python

This is an unoffical api wrapper for tiktok.com in python. With this api you are able to call most trending and fetch specific user information.

## Getting Started

To get started using this api follow the instructions below.

### Prerequisites

You need just python's requests module. If you're not using pip to install.

```
pip install requests
```

### Installing

Clone and just include tiktok.py in your python file

## Quick Start Guide

Explain how to run the automated tests for this system

```
from tiktok import TikTokapi

api = TikTokapi()

# Will Get the 10 most recent trending on the tiktok trending page
api.trending(10)
```

## Detailed Documentation

```
# Where count is how many result you want
# Verbose is optional, default=0. Set it to 1 to get more information
api.trending(count, verbose)
```

Trending returns an array of json objects. Example structure [here](https://gist.github.com/davidteather/0be2e495e2de54098e8f2a9594581d27)
JSON object tree [here](https://gist.github.com/davidteather/bc4baef0edb621dd322c8ad128a31ac1)

```
# Where count is how many result you want
# Verbose is optional, default=0. Set it to 1 to get more information
# userid is the tiktok userid, can be found through response json tree or in the tiktok url
api.userPosts(userid, count, verbose)
```

Trending returns an array of json objects. Example structure [here](https://gist.github.com/davidteather/a5c1e54de353353f77a78139d2e5a9f9)
It has the same JSON object tree as trending. It's [here](https://gist.github.com/davidteather/bc4baef0edb621dd322c8ad128a31ac1) anyways.

## Built With

* [Python 3.7](https://www.python.org/) - The web framework used

## Authors

* **David Teather** - *Initial work* - [davidteather](https://github.com/davidteather)

See also the list of [contributors](https://github.com/davidteather/TikTok-Api/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
