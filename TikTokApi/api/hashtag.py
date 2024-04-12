from __future__ import annotations
from ..exceptions import *

from typing import TYPE_CHECKING, ClassVar, Iterator, Optional

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .video import Video


class Hashtag:
    """
    A TikTok Hashtag/Challenge.

    Example Usage
        .. code-block:: python

            hashtag = api.hashtag(name='funny')
            async for video in hashtag.videos():
                print(video.id)
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

    async def info(self, **kwargs) -> dict:
        """
        Returns all information sent by TikTok related to this hashtag.

        Example Usage
            .. code-block:: python

                hashtag = api.hashtag(name='funny')
                hashtag_data = await hashtag.info()
        """
        if not self.name:
            raise TypeError(
                "You must provide the name when creating this class to use this method."
            )

        url_params = {
            "challengeName": self.name,
            "msToken": kwargs.get("ms_token"),
        }

        resp = await self.parent.make_request(
            url="https://www.tiktok.com/api/challenge/detail/",
            params=url_params,
            headers=kwargs.get("headers"),
            session_index=kwargs.get("session_index"),
        )

        if resp is None:
            raise InvalidResponseException(resp, "TikTok returned an invalid response.")

        self.as_dict = resp
        self.__extract_from_data()
        return resp

    async def videos(self, count=30, cursor=0, **kwargs) -> Iterator[Video]:
        """
        Returns TikTok videos that have this hashtag in the caption.

        Args:
            count (int): The amount of videos you want returned.
            cursor (int): The the offset of videos from 0 you want to get.

        Returns:
            async iterator/generator: Yields TikTokApi.video objects.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                async for video in api.hashtag(name='funny').videos():
                    # do something
        """

        id = getattr(self, "id", None)
        if id is None:
            await self.info(**kwargs)

        found = 0
        while found < count:
            params = {
                "challengeID": self.id,
                "count": 35,
                "cursor": cursor,
            }

            resp = await self.parent.make_request(
                url="https://www.tiktok.com/api/challenge/item_list/",
                params=params,
                headers=kwargs.get("headers"),
                session_index=kwargs.get("session_index"),
            )

            if resp is None:
                raise InvalidResponseException(
                    resp, "TikTok returned an invalid response."
                )

            for video in resp.get("itemList", []):
                yield self.parent.video(data=video)
                found += 1

            if not resp.get("hasMore", False):
                return

            cursor = resp.get("cursor")

    def __extract_from_data(self):
        data = self.as_dict
        keys = data.keys()

        if "title" in keys:
            self.id = data["id"]
            self.name = data["title"]

        if "challengeInfo" in keys:
            if "challenge" in data["challengeInfo"]:
                self.id = data["challengeInfo"]["challenge"]["id"]
                self.name = data["challengeInfo"]["challenge"]["title"]
                self.split_name = data["challengeInfo"]["challenge"].get("splitTitle")

            if "stats" in data["challengeInfo"]:
                self.stats = data["challengeInfo"]["stats"]

        id = getattr(self, "id", None)
        name = getattr(self, "name", None)
        if None in (id, name):
            Hashtag.parent.logger.error(
                f"Failed to create Hashtag with data: {data}\nwhich has keys {data.keys()}"
            )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TikTokApi.hashtag(id='{getattr(self, 'id', None)}', name='{getattr(self, 'name', None)}')"
