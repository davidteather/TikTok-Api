from __future__ import annotations
from os import path

import requests
import logging
import json

from urllib.parse import quote, urlencode

from ..helpers import extract_tag_contents
from ..exceptions import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..tiktok import TikTokApi


class Music():
    parent: TikTokApi

    def __init__(self, music_id: str):
        self.id = music_id

    def music_info(self, use_html=False, **kwargs) -> dict:
        if use_html:
            return self.data_full(**kwargs)['props']['pageProps']['musicInfo']

        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        path = "node/share/music/-{}?{}".format(
            self.id, self.parent._add_url_params()
        )
        res = self.parent.get_data(path, **kwargs)

        if res.get("statusCode", 200) == 10203:
            raise TikTokNotFoundError()

        return res['musicInfo']

    def data_full(self, **kwargs) -> dict:
        r = requests.get(
            "https://www.tiktok.com/music/-{}".format(self.id),
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "User-Agent": self.parent.user_agent,
            },
            proxies=self.parent._format_proxy(kwargs.get("proxy", None)),
            cookies=self.parent.get_cookies(**kwargs),
            **self.parent.requests_extra_kwargs,
        )

        data = extract_tag_contents(r.text)
        return json.loads(data)

    def videos(self, count=30, offset=0, **kwargs) -> dict:
        """Returns a dictionary listing TikToks with a specific sound.

            Note: seems to only support up to ~2,000
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        cursor = offset
        page_size = 30

        while cursor-offset < count:
            query = {
                "secUid": "",
                "musicID": self.id,
                "cursor": cursor,
                "shareUid": "",
                "count": page_size
            }
            path = "api/music/item_list/?{}&{}".format(
                self.parent._add_url_params(), urlencode(query)
            )

            res = self.parent.get_data(path, send_tt_params=True, **kwargs)

            for result in res.get("itemList", []): yield result

            if not res.get("hasMore", False):
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return

            cursor = int(res["cursor"])