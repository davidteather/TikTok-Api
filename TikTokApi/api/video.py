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
    """
    A TikTok Video class

    Example Usage
    ```py
    video = api.video(id='7041997751718137094')
    ```
    """

    parent: ClassVar[TikTokApi]

    id: Optional[str]
    """TikTok's ID of the Video"""
    author: Optional[User]
    """The User who created the Video"""
    sound: Optional[Sound]
    """The Sound that is associated with the Video"""
    hashtags: Optional[list[Hashtag]]
    """A List of Hashtags on the Video"""
    as_dict: dict
    """The raw data associated with this Video."""

    def __init__(
        self,
        id: Optional[str] = None,
        url: Optional[str] = None,
        data: Optional[dict] = None,
    ):
        """
        You must provide the id or a valid url, else this will fail.
        """
        self.id = id
        if data is not None:
            self.as_dict = data
            self.__extract_from_data()
        elif url is not None:
            self.id = extract_video_id_from_url(url)

        if self.id is None:
            raise TypeError("You must provide id or url parameter.")

    def info(self, **kwargs) -> dict:
        """
        Returns a dictionary of TikTok's Video object.

        Example Usage
        ```py
        video_data = api.video(id='7041997751718137094').info()
        ```
        """
        return self.info_full(**kwargs)["itemInfo"]["itemStruct"]

    def info_full(self, **kwargs) -> dict:
        """
        Returns a dictionary of all data associated with a TikTok Video.

        Example Usage
        ```py
        video_data = api.video(id='7041997751718137094').info_full()
        ```
        """
        processed = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = processed.device_id

        device_id = kwargs.get("custom_device_id", None)
        query = {
            "itemId": self.id,
        }
        path = "api/item/detail/?{}&{}".format(
            self.parent._add_url_params(), urlencode(query)
        )

        return self.parent.get_data(path, **kwargs)

    def bytes(self, **kwargs) -> bytes:
        """
        Returns the bytes of a TikTok Video.

        Example Usage
        ```py
        video_bytes = api.video(id='7041997751718137094').bytes()

        # Saving The Video
        with open('saved_video.mp4', 'wb') as output:
            output.write(video_bytes)
        ```
        """
        processed = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = processed.device_id

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
            Video.parent.logger.error(
                f"Failed to create Video with data: {data}\nwhich has keys {data.keys()}"
            )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TikTokApi.video(id='{self.id}')"

    def __getattr__(self, name):
        # Handle author, sound, hashtags, as_dict
        if name in ["author", "sound", "hashtags", "as_dict"]:
            self.as_dict = self.info()
            self.__extract_from_data()
            return self.__getattribute__(name)

        raise AttributeError(f"{name} doesn't exist on TikTokApi.api.Video")
