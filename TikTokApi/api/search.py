from __future__ import annotations

from urllib.parse import urlencode

from typing import TYPE_CHECKING, Generator

from .user import User
from .sound import Sound
from .hashtag import Hashtag

if TYPE_CHECKING:
    from ..tiktok import TikTokApi

import logging
import requests


class Search:
    parent: TikTokApi

    @staticmethod
    def users(search_term, count=28, **kwargs) -> Generator[User, None, None]:
        """Returns a list of users that match the search_term

        ##### Parameters
        * search_term: The string to search for users by
            This string is the term you want to search for users by.

        * count: The number of users to return
            Note: maximum is around 28 for this type of endpoint.
        """
        return Search.discover_type(search_term, prefix="user", count=count, **kwargs)

    @staticmethod
    def sounds(search_term, count=28, **kwargs) -> Generator[Sound, None, None]:
        """Returns a list of sounds that match the search_term

        ##### Parameters
        * search_term: The string to search for sounds by
            This string is the term you want to search for sounds by.

        * count: The number of sounds to return
            Note: maximum is around 28 for this type of endpoint.
        """
        return Search.discover_type(search_term, prefix="music", count=count, **kwargs)

    @staticmethod
    def hashtags(search_term, count=28, **kwargs) -> Generator[Hashtag, None, None]:
        """Returns a list of hashtags that match the search_term

        ##### Parameters
        * search_term: The string to search for hashtags by
            This string is the term you want to search for hashtags by.

        * count: The number of hashtags to return
            Note: maximum is around 28 for this type of endpoint.
        """
        return Search.discover_type(
            search_term, prefix="challenge", count=count, **kwargs
        )

    @staticmethod
    def discover_type(search_term, prefix, count=28, offset=0, **kwargs) -> list:
        """Returns a list of whatever the prefix type you pass in
        ##### Parameters
        * search_term: The string to search by
        * prefix: The prefix of what to search for
        * count: The number search results to return
            Note: maximum is around 28 for this type of endpoint.
        """
        # TODO: Investigate if this is actually working as expected. Doesn't seem to be
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = Search.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        cursor = offset
        page_size = 28

        while cursor - offset < count:
            query = {
                "discoverType": 0,
                "needItemList": False,
                "keyWord": search_term,
                "offset": cursor,
                "count": page_size,
                "useRecommend": False,
                "language": "en",
            }
            path = "api/discover/{}/?{}&{}".format(
                prefix, Search.parent._add_url_params(), urlencode(query)
            )
            data = Search.parent.get_data(path, **kwargs)

            for x in data.get("userInfoList", []):
                yield User(data=x["user"])

            for x in data.get("musicInfoList", []):
                yield Sound(data=x["music"])

            for x in data.get("challengeInfoList", []):
                yield Hashtag(data=x["challenge"])

            if int(data["offset"]) <= offset:
                Search.parent.logger.info(
                    "TikTok is not sending videos beyond this point."
                )
                return

            offset = int(data["offset"])

    @staticmethod
    def users_alternate(search_term, count=28, offset=0, **kwargs) -> list:
        """Returns a list of whatever the prefix type you pass in

        ##### Parameters
        * search_term: The string to search by

        * count: The number search results to return
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = Search.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        cursor = offset

        spawn = requests.head(
            "https://www.tiktok.com",
            proxies=Search.parent._format_proxy(proxy),
            **Search.parent.requests_extra_kwargs
        )
        ttwid = spawn.cookies["ttwid"]

        # For some reason when <= it can be off by one.
        while cursor - offset <= count:
            query = {
                "keyword": search_term,
                "cursor": cursor,
                "app_language": "en",
            }
            path = "api/search/{}/full/?{}&{}".format(
                "user", Search.parent._add_url_params(), urlencode(query)
            )

            data = Search.parent.get_data(
                path, use_desktop_base_url=True, ttwid=ttwid, **kwargs
            )

            # When I move to 3.10+ support make this a match switch.
            for result in data.get("user_list", []):
                yield User(data=result)

            if data.get("has_more", 0) == 0:
                Search.parent.logger.info(
                    "TikTok is not sending videos beyond this point."
                )
                return

            cursor = int(data.get("cursor"))
