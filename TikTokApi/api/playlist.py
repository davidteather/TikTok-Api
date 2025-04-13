from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar, AsyncIterator, Optional
from ..exceptions import InvalidResponseException

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .video import Video
    from .user import User


class Playlist:
    """
    A TikTok video playlist.

    Example Usage:
        .. code-block:: python

            playlist = api.playlist(id='7426714779919797038')
    """

    parent: ClassVar[TikTokApi]

    id: Optional[str]
    """The ID of the playlist."""
    name: Optional[str]
    """The name of the playlist."""
    video_count: Optional[int]
    """The video count of the playlist."""
    creator: Optional[User]
    """The creator of the playlist."""
    cover_url: Optional[str]
    """The cover URL of the playlist."""
    as_dict: dict
    """The raw data associated with this Playlist."""

    def __init__(
        self,
        id: Optional[str] = None,
        data: Optional[dict] = None,
    ):
        """
        You must provide the playlist id or playlist data otherwise this
        will not function correctly.
        """

        if id is None and data.get("id") is None:
            raise TypeError("You must provide id parameter.")

        self.id = id

        if data is not None:
            self.as_dict = data
            self.__extract_from_data()

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

        id = getattr(self, "id", None)
        if not id:
            raise TypeError(
                "You must provide the playlist id when creating this class to use this method."
            )

        url_params = {
            "mixId": id,
            "msToken": kwargs.get("ms_token"),
        }

        resp = await self.parent.make_request(
            url="https://www.tiktok.com/api/mix/detail/",
            params=url_params,
            headers=kwargs.get("headers"),
            session_index=kwargs.get("session_index"),
        )

        if resp is None:
            raise InvalidResponseException(resp, "TikTok returned an invalid response.")

        self.as_dict = resp["mixInfo"]
        self.__extract_from_data()
        return resp

    async def videos(self, count=30, cursor=0, **kwargs) -> AsyncIterator[Video]:
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
        id = getattr(self, "id", None)
        if id is None or id == "":
            await self.info(**kwargs)

        found = 0
        while found < count:
            params = {
              "mixId": id,
              "count": min(count, 30),
              "cursor": cursor,
          }

            resp = await self.parent.make_request(
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
                yield self.parent.video(data=video)
                found += 1

            if not resp.get("hasMore", False):
                return

            cursor = resp.get("cursor")

    def __extract_from_data(self):
        data = self.as_dict
        keys = data.keys()

        if "mixInfo" in keys:
            data = data["mixInfo"]

        self.id = data.get("id", None) or data.get("mixId", None)
        self.name = data.get("name", None) or data.get("mixName", None)
        self.video_count = data.get("videoCount", None)
        self.creator = self.parent.user(data=data.get("creator", {}))
        self.cover_url = data.get("cover", None)

        if None in [self.id, self.name, self.video_count, self.creator, self.cover_url]:
            User.parent.logger.error(
                f"Failed to create Playlist with data: {data}\nwhich has keys {data.keys()}"
            )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        id = getattr(self, "id", None)
        return f"TikTokApi.playlist(id='{id}'')"
