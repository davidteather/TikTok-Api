from __future__ import annotations

from typing import AsyncIterator, TYPE_CHECKING

from ..exceptions import *
from TikTokApi.tiktok_model import TikTokModel

if TYPE_CHECKING:
    from .video import Video


class Hashtag(TikTokModel):
    """
    A TikTok Hashtag/Challenge.

    Example Usage
        .. code-block:: python

            hashtag = api.hashtag(name='funny')
            async for video in hashtag.videos():
                print(video.id)
    """

    id: str | None = None
    """The ID of the hashtag"""

    name: str | None = None
    """The name of the hashtag (omiting the #)"""

    split_name: str | None = None
    """The split name of the hashtag (if it exists)"""

    stats: dict | None = None
    """A dictionary of stats related to this hashtag"""

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

        resp = await self._parent.make_request(
            url="https://www.tiktok.com/api/challenge/detail/",
            params=url_params,
            headers=kwargs.get("headers"),
            session_index=kwargs.get("session_index"),
        )

        if resp is None:
            raise InvalidResponseException(resp, "TikTok returned an invalid response.")

        self._extract_from_data(resp)
        return resp

    async def videos(self, count: int = 30, cursor: int = 0, **kwargs) -> AsyncIterator[Video]:
        """
        Returns TikTok videos that have this hashtag in the caption.

        Args:
            count (int): The amount of videos you want returned.
            cursor (int): The offset of videos from 0 you want to get.

        Returns:
            async iterator/generator: Yields TikTokApi.video objects.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                async for video in api.hashtag(name='funny').videos():
                    # do something
        """

        if self.id is None:
            await self.info(**kwargs)

        found = 0
        while found < count:
            params = {
                "challengeID": self.id,
                "count": 30,
                "cursor": cursor,
            }

            resp = await self._parent.make_request(
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
                yield self._parent.video.from_raw_data(raw_data=video)
                found += 1

            if not resp.get("hasMore", False):
                return

            cursor = resp.get("cursor")

    def _extract_from_data(self, raw_data: dict) -> None:
        self.raw_data = raw_data

        if "title" in raw_data:
            self.id = raw_data["id"]
            self.name = raw_data["title"]

        if "challengeInfo" in raw_data:
            if "challenge" in raw_data["challengeInfo"]:
                self.id = raw_data["challengeInfo"]["challenge"]["id"]
                self.name = raw_data["challengeInfo"]["challenge"]["title"]
                self.split_name = raw_data["challengeInfo"]["challenge"].get("splitTitle")

            if "stats" in raw_data["challengeInfo"]:
                self.stats = raw_data["challengeInfo"]["stats"]

        if None in (self.id, self.name):
            self._parent.logger.error(
                f"Failed to create Hashtag with data: {raw_data}\nwhich has keys {raw_data.keys()}"
            )
