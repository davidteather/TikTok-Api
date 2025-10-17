from __future__ import annotations

from typing import AsyncIterator, TYPE_CHECKING

from ..exceptions import *
from TikTokApi.tiktok_model import TikTokModel

if TYPE_CHECKING:
    from .user import User
    from .video import Video


class Sound(TikTokModel):
    """
    A TikTok Sound/Music/Song.

    Example Usage
        .. code-block:: python

            song = api.song(id='7016547803243022337')
    """

    id: str | None = None
    """TikTok's ID for the sound"""

    title: str | None = None
    """The title of the song."""

    author: User | None = None
    """The author of the song (if it exists)"""

    duration: int | None = None
    """The duration of the song in seconds."""

    original: bool | None = None
    """Whether the song is original or not."""

    play_url: str | None = None
    """The URL to play the sound."""

    cover_large: str | None = None
    """The URL to the cover image of the sound."""

    stats: dict | None = None
    """Statistics related to the sound, such as play count, share count, etc."""

    async def info(self, **kwargs) -> dict:
        """
        Returns all information sent by TikTok related to this sound.

        Returns:
            dict: The raw data returned by TikTok.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                sound_info = await api.sound(id='7016547803243022337').info()
        """

        url_params = {
            "msToken": kwargs.get("ms_token"),
            "musicId": self.id,
        }

        resp = await self._parent.make_request(
            url="https://www.tiktok.com/api/music/detail/",
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
        Returns Video objects of videos created with this sound.

        Args:
            count (int): The amount of videos you want returned.
            cursor (int): The the offset of videos from 0 you want to get.

        Returns:
            async iterator/generator: Yields TikTokApi.video objects.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                async for video in api.sound(id='7016547803243022337').videos():
                    # do something
        """
        if self.id is None:
            raise TypeError(
                "You must provide the id when creating this class to use this method."
            )

        found = 0
        while found < count:
            params = {
                "musicID": self.id,
                "count": 30,
                "cursor": cursor,
            }

            resp = await self._parent.make_request(
                url="https://www.tiktok.com/api/music/item_list/",
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

        if "musicInfo" in raw_data:
            author = raw_data.get("musicInfo").get("author")
            if isinstance(author, dict):
                self.author = self._parent.user.from_raw_data(raw_data=author)
            elif isinstance(author, str):
                self.author = self._parent.user(username=author)

            if raw_data.get("musicInfo").get("music"):
                self.title = raw_data.get("musicInfo").get("music").get("title")
                self.id = raw_data.get("musicInfo").get("music").get("id")
                self.original = raw_data.get("musicInfo").get("music").get("original")
                self.play_url = raw_data.get("musicInfo").get("music").get("playUrl")
                self.cover_large = raw_data.get("musicInfo").get("music").get("coverLarge")
                self.duration = raw_data.get("musicInfo").get("music").get("duration")

        if "music" in raw_data:
            self.title = raw_data.get("music").get("title")
            self.id = raw_data.get("music").get("id")
            self.original = raw_data.get("music").get("original")
            self.play_url = raw_data.get("music").get("playUrl")
            self.cover_large = raw_data.get("music").get("coverLarge")
            self.duration = raw_data.get("music").get("duration")

        if "stats" in raw_data:
            self.stats = raw_data.get("stats")

        if getattr(self, "id", None) is None:
            self._parent.logger.error(f"Failed to create Sound with data: {raw_data}\n")
