from __future__ import annotations
import logging

from urllib.parse import urlencode
from ..exceptions import *

from typing import TYPE_CHECKING, ClassVar, Iterator, Optional

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .video import Video


class Hashtag:
    """
    A TikTok Hashtag/Challenge.

    Example Usage
    ```py
    hashtag = api.hashtag(name='funny')
    ```
    """

    parent: ClassVar[TikTokApi]

    id: Optional[str]
    """The ID of the hashtag"""
    name: Optional[str]
    """The name of the hashtag (omiting the #)"""
    as_dict: dict
    """The raw data associated with this hashtag."""

    def __init__(
        self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        data: Optional[dict] = None,
    ):
        """
        You must provide the name or id of the hashtag.
        """

        if name is not None:
            self.name = name
        if id is not None:
            self.id = id

        if data is not None:
            self.as_dict = data
            self.__extract_from_data()

    def info(self, **kwargs) -> dict:
        """
        Returns TikTok's dictionary representation of the hashtag object.
        """
        return self.info_full(**kwargs)["challengeInfo"]["challenge"]

    def info_full(self, **kwargs) -> dict:
        """
        Returns all information sent by TikTok related to this hashtag.

        Example Usage
        ```py
        hashtag_data = api.hashtag(name='funny').info_full()
        ```
        """
        processed = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = processed.device_id

        if self.name is not None:
            query = {"challengeName": self.name}
        elif self.id is not None:
            query = {"challengeId": self.id}
        else:
            self.parent.logger.warning("Malformed Hashtag Object")
            return {}

        path = "api/challenge/detail/?{}&{}".format(
            self.parent._add_url_params(), urlencode(query)
        )

        data = self.parent.get_data(path, **kwargs)

        if data["challengeInfo"].get("challenge") is None:
            raise NotFoundException("Challenge {} does not exist".format(self.name))

        return data

    def videos(self, count=30, offset=0, **kwargs) -> Iterator[Video]:
        """Returns a dictionary listing TikToks with a specific hashtag.

        - Parameters:
            - count (int): The amount of videos you want returned.
            - offset (int): The the offset of videos from 0 you want to get.

        Example Usage
        ```py
        for video in api.hashtag(name='funny').videos():
            # do something
        ```
        """
        cursor = offset
        page_size = 30
        while cursor - offset < count:
            query = {
                "aid": 1988,
                "count": page_size,
                "challengeID": self.id,
                "cursor": cursor,
            }
            path = "api/challenge/item_list/?{}".format(urlencode(query))
            res = self.parent.get_data_no_sig(path, subdomain="us", **kwargs)
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

        if "title" in keys:
            self.id = data["id"]
            self.name = data["title"]

        if None in (self.name, self.id):
            Hashtag.parent.logger.error(
                f"Failed to create Hashtag with data: {data}\nwhich has keys {data.keys()}"
            )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TikTokApi.hashtag(id='{self.id}', name='{self.name}')"

    def __getattr__(self, name):
        # TODO: Maybe switch to using @property instead
        if name in ["id", "name", "as_dict"]:
            self.as_dict = self.info()
            self.__extract_from_data()
            return self.__getattribute__(name)

        raise AttributeError(f"{name} doesn't exist on TikTokApi.api.Hashtag")
