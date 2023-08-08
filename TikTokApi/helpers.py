from .exceptions import *

import requests
import random


def extract_video_id_from_url(url, headers={}, proxy=None):
    url = requests.head(
        url=url, allow_redirects=True, headers=headers, proxies=proxy
    ).url
    if "@" in url and "/video/" in url:
        return url.split("/video/")[1].split("?")[0]
    else:
        raise TypeError(
            "URL format not supported. Below is an example of a supported url.\n"
            "https://www.tiktok.com/@therock/video/6829267836783971589"
        )


def random_choice(choices: list):
    """Return a random choice from a list, or None if the list is empty"""
    if choices is None or len(choices) == 0:
        return None
    return random.choice(choices)
