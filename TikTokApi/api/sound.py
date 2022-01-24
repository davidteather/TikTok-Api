from __future__ import annotations
from os import path

import requests
import logging
import json

from urllib.parse import quote, urlencode

from ..helpers import extract_tag_contents
from ..exceptions import *

from typing import TYPE_CHECKING, ClassVar, Generator, Optional

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .user import User
    from .video import Video


class Sound:
    parent: ClassVar[TikTokApi]

    id: str
    title: Optional[str]
    author: Optional[User]

    def __init__(self, id: Optional[str] = None, data: Optional[str] = None):
        if data is not None:
            self.as_dict = data
            self.__extract_from_data()
        elif id is None:
            raise TypeError("You must provide id parameter.")
        else:
            self.id = id

    def info(self, use_html=False, **kwargs) -> dict:
        if use_html:
            return self.info_full(**kwargs)["musicInfo"]

        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        path = "node/share/music/-{}?{}".format(self.id, self.parent._add_url_params())
        res = self.parent.get_data(path, **kwargs)

        if res.get("statusCode", 200) == 10203:
            raise TikTokNotFoundError()

        return res["musicInfo"]["music"]

    def info_full(self, **kwargs) -> dict:
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
        return json.loads(data)["props"]["pageProps"]["musicInfo"]

    def videos(self, count=30, offset=0, **kwargs) -> Generator[Video, None, None]:
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

        while cursor - offset < count:
            query = {
                "secUid": "",
                "musicID": self.id,
                "cursor": cursor,
                "shareUid": "",
                "count": page_size,
            }
            path = "api/music/item_list/?{}&{}".format(
                self.parent._add_url_params(), urlencode(query)
            )

            res = self.parent.get_data(path, send_tt_params=True, **kwargs)

            for result in res.get("itemList", []):
                yield self.parent.video(data=result)

            if not res.get("hasMore", False):
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return

            cursor = int(res["cursor"])

    def __extract_from_data(self):
        data = self.as_dict
        keys = data.keys()

        if "authorName" in keys:
            self.id = data["id"]
            self.title = data["title"]

            if data.get("authorName") is not None:
                self.author = self.parent.user(username=data["authorName"])

        if self.id is None:
            logging.error(
                f"Failed to create Sound with data: {data}\nwhich has keys {data.keys()}"
            )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TikTokApi.sound(id='{self.id}')"

    def __getattr__(self, name):
        if name in ["title", "author", "as_dict"]:
            self.as_dict = self.info()
            self.__extract_from_data()
            return self.__getattribute__(name)

        raise AttributeError(f"{name} doesn't exist on TikTokApi.api.Sound")
