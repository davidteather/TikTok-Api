from __future__ import annotations

from urllib.parse import quote, urlencode

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..tiktok import TikTokApi

import logging
import requests

class Search():
    parent: TikTokApi

    def __init__(self, parent: TikTokApi):
        Search.parent = parent

    def users(self, search_term, count=28, **kwargs) -> list:
        """Returns a list of users that match the search_term

        ##### Parameters
        * search_term: The string to search for users by
            This string is the term you want to search for users by.

        * count: The number of users to return
            Note: maximum is around 28 for this type of endpoint.
        """
        return self.discover_type(search_term, prefix="user", count=count, **kwargs)

    def music(self, search_term, count=28, **kwargs) -> list:
        """Returns a list of music that match the search_term

        ##### Parameters
        * search_term: The string to search for music by
            This string is the term you want to search for music by.

        * count: The number of music to return
            Note: maximum is around 28 for this type of endpoint.
        """
        return self.discover_type(search_term, prefix="music", count=count, **kwargs)

    def hashtags(self, search_term, count=28, **kwargs) -> list:
        """Returns a list of hashtags that match the search_term

        ##### Parameters
        * search_term: The string to search for music by
            This string is the term you want to search for music by.

        * count: The number of music to return
            Note: maximum is around 28 for this type of endpoint.
        """
        return self.discover_type(
            search_term, prefix="challenge", count=count, **kwargs
        )

    def discover_type(self, search_term, prefix, count=28, offset=0, **kwargs) -> list:
        """Returns a list of whatever the prefix type you pass in

        ##### Parameters
        * search_term: The string to search by

        * prefix: The prefix of what to search for

        * count: The number search results to return
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

        spawn = requests.head(
            "https://www.tiktok.com",
            proxies=self.parent._format_proxy(proxy),
            **self.parent.requests_extra_kwargs
        )
        ttwid = spawn.cookies["ttwid"]

        while cursor-offset < count:
            query = {
                "keyword": search_term,
                "cursor": cursor,
                "app_language": "en",
            }
            path = "api/search/{}/full/?{}&{}".format(
                prefix, self.parent._add_url_params(), urlencode(query)
            )

            data = self.parent.get_data(path, use_desktop_base_url=True, ttwid=ttwid, **kwargs)

            # When I move to 3.10+ support make this a match switch.
            if prefix == 'user':
                cursor += len(data.get("user_list", []))
                for result in data.get("user_list", []): yield result
            elif prefix == 'music':
                cursor += len(data.get("music_list", []))
                for result in data.get("music_list", []): yield result
            elif prefix == 'challenge':
                cursor += len(data.get("challenge_list", []))
                for result in data.get("challenge_list", []): yield result

            if data.get('has_more', 0) == 0:
                logging.info("TikTok is not sending videos beyond this point.")
                return