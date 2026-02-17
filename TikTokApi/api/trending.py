from __future__ import annotations

from typing import AsyncIterator, TYPE_CHECKING

from ..exceptions import InvalidResponseException
from TikTokApi.tiktok_model import TikTokApiRoute

if TYPE_CHECKING:
    from .video import Video


class Trending(TikTokApiRoute):
    """Contains static methods related to trending objects on TikTok."""

    @classmethod
    async def videos(cls, count: int = 30, **kwargs) -> AsyncIterator[Video]:
        """
        Returns Videos that are trending on TikTok.

        Args:
            count (int): The amount of videos you want returned.

        Returns:
            async iterator/generator: Yields TikTokApi.video objects.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                async for video in api.trending.videos():
                    # do something
        """

        found = 0
        while found < count:
            params = {
                "from_page": "fyp",
                "count": 12,  # TikTok expects this number to ALWAYS be 12, regardless of how many you want
            }

            resp = await cls._parent.make_request(
                url="https://www.tiktok.com/api/recommend/item_list/",
                params=params,
                headers=kwargs.get("headers"),
                session_index=kwargs.get("session_index"),
            )

            if resp is None:
                raise InvalidResponseException(
                    resp, "TikTok returned an invalid response."
                )

            for video in resp.get("itemList", []):
                yield cls._parent.video.from_raw_data(raw_data=video)
                found += 1

            if not resp.get("hasMore", False):
                return
