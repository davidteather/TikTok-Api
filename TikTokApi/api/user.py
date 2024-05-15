from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar, Iterator, Optional
from ..exceptions import InvalidResponseException

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .video import Video


class User:
    """
    A TikTok User.

    Example Usage:
        .. code-block:: python

            user = api.user(username='therock')
    """

    parent: ClassVar[TikTokApi]

    user_id: str
    """The  ID of the user."""
    sec_uid: str
    """The sec UID of the user."""
    username: str
    """The username of the user."""
    as_dict: dict
    """The raw data associated with this user."""

    def __init__(
        self,
        username: Optional[str] = None,
        user_id: Optional[str] = None,
        sec_uid: Optional[str] = None,
        data: Optional[dict] = None,
    ):
        """
        You must provide the username or (user_id and sec_uid) otherwise this
        will not function correctly.
        """
        self.__update_id_sec_uid_username(user_id, sec_uid, username)
        if data is not None:
            self.as_dict = data
            self.__extract_from_data()

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

        username = getattr(self, "username", None)
        if not username:
            raise TypeError(
                "You must provide the username when creating this class to use this method."
            )

        sec_uid = getattr(self, "sec_uid", None)
        url_params = {
            "secUid": sec_uid if sec_uid is not None else "",
            "uniqueId": username,
            "msToken": kwargs.get("ms_token"),
        }

        resp = await self.parent.make_request(
            url="https://www.tiktok.com/api/user/detail/",
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
        Returns a user's videos.

        Args:
            count (int): The amount of videos you want returned.
            cursor (int): The the offset of videos from 0 you want to get.

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

            resp = await self.parent.make_request(
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
                yield self.parent.video(data=video)
                found += 1

            if not resp.get("hasMore", False):
                return

            cursor = resp.get("cursor")

    async def liked(
        self, count: int = 30, cursor: int = 0, **kwargs
    ) -> Iterator[Video]:
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

            resp = await self.parent.make_request(
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
                yield self.parent.video(data=video)
                found += 1

            if not resp.get("hasMore", False):
                return

            cursor = resp.get("cursor")

    def __extract_from_data(self):
        data = self.as_dict
        keys = data.keys()

        if "userInfo" in keys:
            self.__update_id_sec_uid_username(
                data["userInfo"]["user"]["id"],
                data["userInfo"]["user"]["secUid"],
                data["userInfo"]["user"]["uniqueId"],
            )
        else:
            self.__update_id_sec_uid_username(
                data["id"],
                data["secUid"],
                data["uniqueId"],
            )

        if None in (self.username, self.user_id, self.sec_uid):
            User.parent.logger.error(
                f"Failed to create User with data: {data}\nwhich has keys {data.keys()}"
            )

    def __update_id_sec_uid_username(self, id, sec_uid, username):
        self.user_id = id
        self.sec_uid = sec_uid
        self.username = username

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        username = getattr(self, "username", None)
        user_id = getattr(self, "user_id", None)
        sec_uid = getattr(self, "sec_uid", None)
        return f"TikTokApi.user(username='{username}', user_id='{user_id}', sec_uid='{sec_uid}')"
