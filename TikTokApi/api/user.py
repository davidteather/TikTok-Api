from __future__ import annotations

from typing import AsyncIterator, TYPE_CHECKING

from ..exceptions import InvalidResponseException
from TikTokApi.tiktok_model import TikTokModel

if TYPE_CHECKING:
    from .playlist import Playlist
    from .video import Video


class User(TikTokModel):
    """
    A TikTok User.

    Example Usage:
        .. code-block:: python

            user = api.user(username='therock')
    """

    username: str | None = None
    """The username of the user."""

    user_id: str | None = None
    """The  ID of the user."""

    sec_uid: str | None = None
    """The sec UID of the user."""

    async def info(self, **kwargs) -> dict:
        """
        Returns a dictionary of information associated with this User.

        Returns:
            dict: A dictionary of information associated with this User.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                user_data = await api.user(username='therock').info()
        """

        if not self.username:
            raise TypeError(
                "You must provide the username when creating this class to use this method."
            )

        url_params = {
            "secUid": self.sec_uid if self.sec_uid is not None else "",
            "uniqueId": self.username,
            "msToken": kwargs.get("ms_token"),
        }

        resp = await self._parent.make_request(
            url="https://www.tiktok.com/api/user/detail/",
            params=url_params,
            headers=kwargs.get("headers"),
            session_index=kwargs.get("session_index"),
        )

        if resp is None:
            raise InvalidResponseException(resp, "TikTok returned an invalid response.")

        self._extract_from_data(resp)
        return resp

    async def playlists(self, count: int = 20, cursor: int = 0, **kwargs) -> AsyncIterator["Playlist"]:
        """
        Returns a user's playlists.

        Returns:
            async iterator/generator: Yields TikTokApi.playlist objects.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                async for playlist in await api.user(username='therock').playlists():
                    # do something
        """

        sec_uid = getattr(self, "sec_uid", None)
        if sec_uid is None or sec_uid == "":
            await self.info(**kwargs)
        found = 0

        while found < count:
            params = {
                "secUid": self.sec_uid,
                "count": min(count, 20),
                "cursor": cursor,
            }

            resp = await self._parent.make_request(
                url="https://www.tiktok.com/api/user/playlist",
                params=params,
                headers=kwargs.get("headers"),
                session_index=kwargs.get("session_index"),
            )

            if resp is None:
                raise InvalidResponseException(
                    resp, "TikTok returned an invalid response."
                )

            for playlist in resp.get("playList", []):
                yield self._parent.playlist.from_raw_data(raw_data=playlist)
                found += 1

            if not resp.get("hasMore", False):
                return

            cursor = resp.get("cursor")

    async def videos(self, count: int = 30, cursor: int = 0, **kwargs) -> AsyncIterator["Video"]:
        """
        Returns a user's videos.

        Args:
            count (int): The amount of videos you want returned.
            cursor (int): The offset of videos from 0 you want to get.

        Returns:
            async iterator/generator: Yields TikTokApi.video objects.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                async for video in api.user(username="davidteathercodes").videos():
                    # do something
        """
        sec_uid = getattr(self, "sec_uid", None)
        if sec_uid is None or sec_uid == "":
            await self.info(**kwargs)

        found = 0
        while found < count:
            params = {
                "secUid": self.sec_uid,
                "count": 35,
                "cursor": cursor,
            }

            resp = await self._parent.make_request(
                url="https://www.tiktok.com/api/post/item_list/",
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

    async def liked(self, count: int = 30, cursor: int = 0, **kwargs) -> AsyncIterator["Video"]:
        """
        Returns a user's liked posts if public.

        Args:
            count (int): The amount of recent likes you want returned.
            cursor (int): The the offset of likes from 0 you want to get.

        Returns:
            async iterator/generator: Yields TikTokApi.video objects.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, the user's likes are private, or one we don't understand.

        Example Usage:
            .. code-block:: python

                async for like in api.user(username="davidteathercodes").liked():
                    # do something
        """
        sec_uid = getattr(self, "sec_uid", None)
        if sec_uid is None or sec_uid == "":
            await self.info(**kwargs)

        found = 0
        while found < count:
            params = {
                "secUid": self.sec_uid,
                "count": 35,
                "cursor": cursor,
            }

            resp = await self._parent.make_request(
                url="https://www.tiktok.com/api/favorite/item_list",
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
        """
        Extracts relevant fields from the raw_data dictionary and assigns them to class attributes.

        """

        self.raw_data = raw_data

        if "userInfo" in raw_data:
            self.user_id = raw_data["userInfo"]["user"]["id"]
            self.sec_uid = raw_data["userInfo"]["user"]["secUid"]
            self.username = raw_data["userInfo"]["user"]["uniqueId"]
        else:
            self.user_id = raw_data.get("id")
            self.sec_uid = raw_data.get("secUid")
            self.username = raw_data.get("uniqueId")

        if None in (self.username, self.user_id, self.sec_uid):
            self._parent.logger.error(
                f"Failed to create User with data: {raw_data}\nwhich has keys {raw_data.keys()}"
            )
