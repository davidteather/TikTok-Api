from __future__ import annotations
import logging

from urllib.parse import urlencode
from ..exceptions import *

from typing import TYPE_CHECKING, Generator, Optional

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .video import Video


class Hashtag:
    parent: TikTokApi

    def __init__(
        self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        data: Optional[str] = None,
    ):
        self.as_dict = data
        self.name = name
        self.id = id
        if data is not None:
            self.__extract_from_data()

    def info(self, **kwargs) -> dict:
        return self.info_full(**kwargs)["challengeInfo"]["challenge"]

    def info_full(self, **kwargs) -> dict:
        """Returns a hashtag object.

        ##### Parameters
        * hashtag: The hashtag to search by

            Without the # symbol
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        if self.name:
            query = {"challengeName": self.name}
        else:
            query = {"challengeId": self.id}
        path = "api/challenge/detail/?{}&{}".format(
            self.parent._add_url_params(), urlencode(query)
        )

        data = self.parent.get_data(path, **kwargs)

        if data["challengeInfo"].get("challenge") is None:
            raise TikTokNotFoundError("Challenge {} does not exist".format(self.name))

        return data

    def videos(self, count=30, offset=0, **kwargs) -> Generator[Video, None, None]:
        """Returns a dictionary listing TikToks with a specific hashtag.

        ##### Parameters
        * count: The number of posts to return
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

        if self.id is None:
            self.id = self.info()["id"]

        cursor = offset
        page_size = 30

        while cursor - offset < count:
            query = {
                "count": page_size,
                "challengeID": self.id,
                "cursor": cursor,
            }
            path = "api/challenge/item_list/?{}&{}".format(
                self.parent._add_url_params(), urlencode(query)
            )
            res = self.parent.get_data(path, **kwargs)

            for result in res.get("itemList", []):
                yield self.parent.video(data=result)

            if not res.get("hasMore", False):
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return

            cursor = int(res["cursor"])

    def __extract_from_data(self):
        data = self.as_dict
        keys = data.keys()

        if "title" in keys:
            self.id = data["id"]
            self.name = data["title"]

        if None in (self.name, self.id):
            logging.error(
                f"Failed to create Hashtag with data: {data}\nwhich has keys {data.keys()}"
            )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TikTokApi.hashtag(id='{self.id}', name='{self.name}')"
