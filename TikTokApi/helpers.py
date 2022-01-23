from TikTokApi.browser_utilities.browser import browser
from urllib.parse import quote, urlencode
from .exceptions import *

import re
import requests


def extract_tag_contents(html):
    next_json = re.search(
        r"id=\"__NEXT_DATA__\"\s+type=\"application\/json\"\s*[^>]+>\s*(?P<next_data>[^<]+)",
        html,
    )
    if next_json:
        nonce_start = '<head nonce="'
        nonce_end = '">'
        nonce = html.split(nonce_start)[1].split(nonce_end)[0]
        j_raw = html.split(
            '<script id="__NEXT_DATA__" type="application/json" nonce="%s" crossorigin="anonymous">'
            % nonce
        )[1].split("</script>")[0]
        return j_raw
    else:
        sigi_json = re.search(
            r'>\s*window\[[\'"]SIGI_STATE[\'"]\]\s*=\s*(?P<sigi_state>{.+});', html
        )
        if sigi_json:
            return sigi_json.group(1)
        else:
            raise TikTokCaptchaError()


def extract_video_id_from_url(url):
    url = requests.head(url=url, allow_redirects=True).url
    if "@" in url and "/video/" in url:
        return url.split("/video/")[1].split("?")[0]
    else:
        raise TypeError(
            "URL format not supported. Below is an example of a supported url.\n"
            "https://www.tiktok.com/@therock/video/6829267836783971589"
        )
