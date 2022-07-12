from __future__ import annotations
from os import path

import requests
import json

from urllib.parse import quote, urlencode

from ..helpers import extract_tag_contents
from ..exceptions import *

from typing import TYPE_CHECKING, ClassVar, Iterator, Optional

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .user import User
    from .video import Video


class Sound:
    """
    A TikTok Sound/Music/Song.

    Example Usage
    ```py
    song = api.song(id='7016547803243022337')
    ```
    """

    parent: ClassVar[TikTokApi]

    id: str
    """TikTok's ID for the sound"""
    title: Optional[str]
    """The title of the song."""
    author: Optional[User]
    """The author of the song (if it exists)"""

    def __init__(self, id: Optional[str] = None, data: Optional[str] = None):
        """
        You must provide the id of the sound or it will not work.
        """
        if data is not None:
            self.as_dict = data
            self.__extract_from_data()
        elif id is None:
            raise TypeError("You must provide id parameter.")
        else:
            self.id = id

    def info(self, use_html=False, **kwargs) -> dict:
        """
        Returns a dictionary of TikTok's Sound/Music object.

        - Parameters:
            - use_html (bool): If you want to perform an HTML request or not.
                Defaults to False to use an API call, which shouldn't get detected
                as often as an HTML request.


        Example Usage
        ```py
        sound_data = api.sound(id='7016547803243022337').info()
        ```
        """
        self.__ensure_valid()
        if use_html:
            return self.info_full(**kwargs)["musicInfo"]

        processed = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = processed.device_id

        path = "node/share/music/-{}?{}".format(self.id, self.parent._add_url_params())
        res = self.parent.get_data(path, **kwargs)

        if res.get("statusCode", 200) == 10203:
            raise NotFoundException()

        return res["musicInfo"]["music"]

    def info_full(self, **kwargs) -> dict:
        """
        Returns all the data associated with a TikTok Sound.

        This makes an API request, there is no HTML request option, as such
        with Sound.info()

        Example Usage
        ```py
        sound_data = api.sound(id='7016547803243022337').info_full()
        ```
        """
        self.__ensure_valid()
        r = requests.get(
            "https://www.tiktok.com/music/-{}".format(self.id),
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "User-Agent": self.parent._user_agent,
            },
            proxies=self.parent._format_proxy(kwargs.get("proxy", None)),
            cookies=self.parent._get_cookies(**kwargs),
            **self.parent._requests_extra_kwargs,
        )

        data = extract_tag_contents(r.text)
        return json.loads(data)["props"]["pageProps"]["musicInfo"]

    def videos(self, count=30, offset=0, **kwargs) -> Iterator[Video]:
        """
        Returns Video objects of videos created with this sound.

        - Parameters:
            - count (int): The amount of videos you want returned.
            - offset (int): The offset of videos you want returned.

        Example Usage
        ```py
        for video in api.sound(id='7016547803243022337').videos():
            # do something
        ```
        """
        self.__ensure_valid()
        processed = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = processed.device_id

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
                self.parent.logger.info(
                    "TikTok isn't sending more TikToks beyond this point."
                )
                return

            cursor = int(res["cursor"])

    def __extract_from_data(self):
        data = self.as_dict
        keys = data.keys()

        if data.get("id") == "":
            self.id = ""

        if "authorName" in keys:
            self.id = data["id"]
            self.title = data["title"]

            if data.get("authorName") is not None:
                self.author = self.parent.user(username=data["authorName"])

        if self.id is None:
            Sound.parent.logger.error(
                f"Failed to create Sound with data: {data}\nwhich has keys {data.keys()}"
            )

    def __ensure_valid(self):
        if self.id == "":
            raise SoundRemovedException(0, None, "This sound has been removed!")

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
