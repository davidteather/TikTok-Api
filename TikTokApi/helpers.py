from .exceptions import *

import requests
import random


def extract_video_id_from_url(url, headers={}, proxy=None):
    url = requests.head(
        url=url, allow_redirects=True, headers=headers, proxies=proxy
    ).url
    if "@" in url:
        for post_type in ("video", "photo"):
            marker = f"/{post_type}/"
            if marker in url:
                return url.split(marker, 1)[1].split("?", 1)[0]

    raise TypeError(
        "URL format not supported. Expected a TikTok /video/ or /photo/ post URL.\n"
        "https://www.tiktok.com/@therock/video/6829267836783971589"
    )


def random_choice(choices: list):
    """Return a random choice from a list, or None if the list is empty"""
    if choices is None or len(choices) == 0:
        return None
    return random.choice(choices)


def requests_cookie_to_playwright_cookie(req_c):
    c = {
        "name": req_c.name,
        "value": req_c.value,
        "domain": req_c.domain,
        "path": req_c.path,
        "secure": req_c.secure,
    }
    if req_c.expires:
        c["expires"] = req_c.expires
    return c
