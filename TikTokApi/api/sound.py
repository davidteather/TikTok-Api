from __future__ import annotations
from ..exceptions import *
from typing import TYPE_CHECKING, ClassVar, Iterator, Optional

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .user import User
    from .video import Video


class Sound:
    """
    A TikTok Sound/Music/Song.

    Example Usage
        .. code-block:: python

            song = api.song(id='7016547803243022337')
    """

    parent: ClassVar[TikTokApi]

    id: str
    """TikTok's ID for the sound"""
    title: Optional[str]
    """The title of the song."""
    author: Optional[User]
    """The author of the song (if it exists)"""
    duration: Optional[int]
    """The duration of the song in seconds."""
    original: Optional[bool]
    """Whether the song is original or not."""

    def __init__(self, id: Optional[str] = None, data: Optional[str] = None):
        """
        You must provide the id of the sound or it will not work.
        """
        if data is not None:
            self.as_dict = data
            self.__extract_from_data()
        elif id is None:
            raise TypeError("You must provide id parameter.")
        else:
            self.id = id

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

        id = getattr(self, "id", None)
        if not id:
            raise TypeError(
                "You must provide the id when creating this class to use this method."
            )

        url_params = {
            "msToken": kwargs.get("ms_token"),
            "musicId": id,
        }

        resp = await self.parent.make_request(
            url="https://www.tiktok.com/api/music/detail/",
            params=url_params,
            headers=kwargs.get("headers"),
            session_index=kwargs.get("session_index"),
        )

        if resp is None:
            raise InvalidResponseException(resp, "TikTok returned an invalid response.")

        self.as_dict = resp
        self.__extract_from_data()
        return resp

    async def videos(self, count=30, cursor=0, **kwargs) -> AsyncIterator[Video]:
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
        id = getattr(self, "id", None)
        if id is None:
            raise TypeError(
                "You must provide the id when creating this class to use this method."
            )

        found = 0
        while found < count:
            params = {
                "musicID": id,
                "count": 30,
                "cursor": cursor,
            }

            resp = await self.parent.make_request(
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
                yield self.parent.video(data=video)
                found += 1

            if not resp.get("hasMore", False):
                return

            cursor = resp.get("cursor")

    def __extract_from_data(self):
        data = self.as_dict
        keys = data.keys()

        if "musicInfo" in keys:
            author = data.get("musicInfo").get("author")
            if isinstance(author, dict):
                self.author = self.parent.user(data=author)
            elif isinstance(author, str):
                self.author = self.parent.user(username=author)

            if data.get("musicInfo").get("music"):
                self.title = data.get("musicInfo").get("music").get("title")
                self.id = data.get("musicInfo").get("music").get("id")
                self.original = data.get("musicInfo").get("music").get("original")
                self.play_url = data.get("musicInfo").get("music").get("playUrl")
                self.cover_large = data.get("musicInfo").get("music").get("coverLarge")
                self.duration = data.get("musicInfo").get("music").get("duration")

        if "music" in keys:
            self.title = data.get("music").get("title")
            self.id = data.get("music").get("id")
            self.original = data.get("music").get("original")
            self.play_url = data.get("music").get("playUrl")
            self.cover_large = data.get("music").get("coverLarge")
            self.duration = data.get("music").get("duration")

        if "stats" in keys:
            self.stats = data.get("stats")

        if getattr(self, "id", None) is None:
            Sound.parent.logger.error(f"Failed to create Sound with data: {data}\n")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TikTokApi.sound(id='{getattr(self, 'id', None)}')"
