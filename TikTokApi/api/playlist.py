from __future__ import annotations

from typing import AsyncIterator, TYPE_CHECKING

from .video import Video
from ..exceptions import InvalidResponseException
from TikTokApi.tiktok_model import TikTokModel

if TYPE_CHECKING:
    from .user import User


class Playlist(TikTokModel):
    """
    A TikTok video playlist.

    Example Usage:
        .. code-block:: python

            playlist = api.playlist(id='7426714779919797038')
    """

    id: str | None = None
    """The ID of the playlist."""

    name: str | None = None
    """The name of the playlist."""

    video_count: int | None = None
    """The video count of the playlist."""

    creator: User | None = None
    """The creator of the playlist."""

    cover_url: str | None = None
    """The cover URL of the playlist."""

    async def info(self, **kwargs) -> dict:
        """
        Returns a dictionary of information associated with this Playlist.

        Returns:
            dict: A dictionary of information associated with this Playlist.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                user_data = await api.playlist(id='7426714779919797038').info()
        """

        url_params = {
            "mixId": self.id,
            "msToken": kwargs.get("ms_token"),
        }

        resp = await self._parent.make_request(
            url="https://www.tiktok.com/api/mix/detail/",
            params=url_params,
            headers=kwargs.get("headers"),
            session_index=kwargs.get("session_index"),
        )

        if resp is None:
            raise InvalidResponseException(resp, "TikTok returned an invalid response.")

        self._extract_from_data(resp)
        return resp

    async def videos(self, count=30, cursor=0, **kwargs) -> AsyncIterator["Video"]:
        """
        Returns an iterator of videos in this User's playlist.

        Returns:
            Iterator[dict]: An iterator of videos in this User's playlist.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                playlist_videos = await api.playlist(id='7426714779919797038').videos()
        """

        found = 0
        while found < count:
            params = {
                "mixId": self.id,
                "count": min(count, 30),
                "cursor": cursor,
            }

            resp = await self._parent.make_request(
                url="https://www.tiktok.com/api/mix/item_list/",
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

        if "mixInfo" in raw_data:
            raw_data = raw_data["mixInfo"]

        video_id: str | None = raw_data.get("id", None) or raw_data.get("mixId", None)

        if video_id is None:
            self._parent.logger.error(f"Failed to create Playlist with data: {raw_data}\nwhich has keys {raw_data.keys()}")
            return

        self.id = video_id
        self.name = raw_data.get("name", None) or raw_data.get("mixName", None)
        self.video_count = raw_data.get("videoCount", None)
        self.creator = self._parent.user.from_raw_data(raw_data=raw_data.get("creator", {}))
        self.cover_url = raw_data.get("cover", None)

        if None in [self.name, self.video_count, self.creator, self.cover_url]:
            self._parent.logger.error(
                f"Failed to create Playlist with data: {raw_data}\nwhich has keys {raw_data.keys()}"
            )
