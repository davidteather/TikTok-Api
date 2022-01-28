from __future__ import annotations

import logging
import requests
from urllib.parse import urlencode

from .video import Video
from .sound import Sound
from .user import User
from .hashtag import Hashtag

from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from ..tiktok import TikTokApi


class Trending:
    """Contains static methods related to trending."""

    parent: TikTokApi

    @staticmethod
    def users(**kwargs) -> Iterator[User]:
        """
        Trending users

        Example Usage
        ```py
        for user in api.trending.users('therock'):
            # do something
        ```
        """
        return Trending.discover_type(prefix="user", **kwargs)

    @staticmethod
    def sounds(**kwargs) -> Iterator[Sound]:
        """
        Trending sounds

        Example Usage
        ```py
        for user in api.trending.sounds('funny'):
            # do something
        ```
        """
        return Trending.discover_type(prefix="music", **kwargs)

    @staticmethod
    def hashtags(**kwargs) -> Iterator[Hashtag]:
        """
        Trending hashtags

        Example Usage
        ```py
        for user in api.trending.hashtags('funny'):
            # do something
        ```
        """
        return Trending.discover_type(prefix="challenge", **kwargs)

    @staticmethod
    def discover_type(prefix, count=28, offset=0, **kwargs) -> Iterator:
        """
        Returns trending objects.

        You should instead use the users/sounds/hashtags as they all use data
        from this function.

        - Parameters:
            - search_term (str): The phrase you want to search for.
            - prefix (str): either user|music|challenge

        Example Usage
        ```py
        for user in api.search.discover_type('therock', 'user'):
            # do something
        ```

        """
        # TODO: Investigate if this is actually working as expected. Doesn't seem to be, check offset
        processed = Trending.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = processed.device_id

        cursor = offset
        page_size = 28

        while cursor - offset < count:
            query = {
                "discoverType": 0,
                "needItemList": False,
                "keyWord": "f",  # Keyword is a required param, but doesn't do anything anymore.
                "offset": cursor,
                "count": page_size,
                "useRecommend": False,
                "language": "en",
            }
            path = "node/share/discover/{}/?{}&{}".format(
                prefix, Trending.parent._add_url_params(), urlencode(query)
            )
            data = Trending.parent.get_data(path, **kwargs)

            for x in data.get("userInfoList", []):
                yield User(data=x["user"])

            for x in data.get("musicInfoList", []):
                yield Sound(data=x["music"])

            for x in data.get("challengeInfoList", []):
                yield Hashtag(data=x["challenge"])

            if int(data["offset"]) <= offset:
                Trending.parent.logger.info(
                    "TikTok is not sending videos beyond this point."
                )
                return

            offset = int(data["offset"])

    @staticmethod
    def videos(count=30, **kwargs) -> Iterator[Video]:
        """
        Returns Videos that are trending on TikTok.

        - Parameters:
            - count (int): The amount of videos you want returned.
        """

        processed = Trending.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = processed.device_id

        spawn = requests.head(
            "https://www.tiktok.com",
            proxies=Trending.parent._format_proxy(processed.proxy),
            **Trending.parent.requests_extra_kwargs,
        )
        ttwid = spawn.cookies["ttwid"]

        first = True
        amount_yielded = 0

        while amount_yielded < count:
            query = {
                "count": 30,
                "id": 1,
                "sourceType": 12,
                "itemID": 1,
                "insertedItemID": "",
                "region": processed.region,
                "priority_region": processed.region,
                "language": processed.language,
            }
            path = "api/recommend/item_list/?{}&{}".format(
                Trending.parent._add_url_params(), urlencode(query)
            )
            res = Trending.parent.get_data(path, ttwid=ttwid, **kwargs)
            for result in res.get("itemList", []):
                yield Video(data=result)
            amount_yielded += len(res.get("itemList", []))

            if not res.get("hasMore", False) and not first:
                Trending.parent.logger.info(
                    "TikTok isn't sending more TikToks beyond this point."
                )
                return

            first = False
