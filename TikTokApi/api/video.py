from __future__ import annotations

from urllib.parse import urlencode

from ..helpers import extract_video_id_from_url

import logging
from typing import TYPE_CHECKING, ClassVar, Optional

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .user import User
    from .sound import Sound
    from .hashtag import Hashtag


class Video:
    """A TikTok Video class

    Attributes
        id: The TikTok video ID.
        author: The author of the TikTok as a User object.
        as_dict: The dictionary provided to create the class.
    """

    parent: ClassVar[TikTokApi]

    id: str
    author: Optional[User]
    sound: Optional[Sound]
    hashtags: Optional[list[Hashtag]]
    as_dict: dict

    def __init__(
        self,
        id: Optional[str] = None,
        url: Optional[str] = None,
        data: Optional[dict] = None,
    ):
        self.id = id
        self.as_dict = data
        if data is not None:
            self.__extract_from_data()
        elif url is not None:
            self.id = extract_video_id_from_url(url)

        if self.id is None:
            raise TypeError("You must provide id or url parameter.")

    def info(self, **kwargs) -> dict:
        return self.info_full(**kwargs)["itemInfo"]["itemStruct"]

    def info_full(self, **kwargs) -> dict:
        """Returns a dictionary of a specific TikTok."""
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        device_id = kwargs.get("custom_device_id", None)
        query = {
            "itemId": self.id,
        }
        path = "api/item/detail/?{}&{}".format(
            self.parent._add_url_params(), urlencode(query)
        )

        return self.parent.get_data(path, **kwargs)

    def bytes(self, **kwargs) -> bytes:
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        video_data = self.info(**kwargs)
        download_url = video_data["video"]["playAddr"]

        return self.parent.get_bytes(url=download_url, **kwargs)

    def __extract_from_data(self) -> None:
        data = self.as_dict
        keys = data.keys()

        if "author" in keys:
            self.id = data["id"]
            self.author = self.parent.user(data=data["author"])
            self.sound = self.parent.sound(data=data["music"])

            self.hashtags = [
                self.parent.hashtag(data=hashtag)
                for hashtag in data.get("challenges", [])
            ]

        if self.id is None:
            logging.error(
                f"Failed to create Video with data: {data}\nwhich has keys {data.keys()}"
            )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TikTokApi.video(id='{self.id}')"
