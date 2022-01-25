from __future__ import annotations

import logging
import requests
from urllib.parse import urlencode

from .video import Video

from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    from ..tiktok import TikTokApi


class Trending:
    parent: TikTokApi

    @staticmethod
    def videos(count=30, **kwargs) -> Generator[Video, None, None]:
        """
        Gets trending TikToks

        ##### Parameters
        * count: The amount of TikToks you want returned, optional

            Note: TikTok seems to only support at MOST ~2000 TikToks
            from a single endpoint.
        """

        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = Trending.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        spawn = requests.head(
            "https://www.tiktok.com",
            proxies=Trending.parent._format_proxy(proxy),
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
                "region": region,
                "priority_region": region,
                "language": language,
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
