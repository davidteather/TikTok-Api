from __future__ import annotations

from typing import AsyncIterator, TYPE_CHECKING

from ..exceptions import InvalidResponseException
from TikTokApi.tiktok_model import TikTokApiRoute

if TYPE_CHECKING:
    from .user import User


class Search(TikTokApiRoute):
    """Contains static methods about searching TikTok for a phrase."""

    @classmethod
    async def users(cls, search_term: str, count: int = 10, cursor: int = 0, **kwargs) -> AsyncIterator["User"]:
        """
        Searches for users.

        Note: Your ms_token needs to have done a search before for this to work.

        Args:
            search_term (str): The phrase you want to search for.
            count (int): The amount of users you want returned.
            cursor (int): The cursor to start from.

        Returns:
            async iterator/generator: Yields TikTokApi.user objects.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                async for user in api.search.users('david teather'):
                    # do something
        """
        async for user in cls.search_type(
                search_term, "user", count=count, cursor=cursor, **kwargs
        ):
            yield user

    @classmethod
    async def search_type(cls, search_term, obj_type, count=10, cursor=0, **kwargs) -> AsyncIterator:
        """
        Searches for a specific type of object. But you shouldn't use this directly, use the other methods.

        Note: Your ms_token needs to have done a search before for this to work.
        Note: Currently only supports searching for users, other endpoints require auth.

        Args:
            search_term (str): The phrase you want to search for.
            obj_type (str): The type of object you want to search for (user)
            count (int): The amount of users you want returned.
            cursor (int): The offset of users from 0 you want to get.

        Returns:
            async iterator/generator: Yields TikTokApi.video objects.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                async for user in api.search.search_type('david teather', 'user'):
                    # do something
        """
        found = 0
        while found < count:
            params = {
                "keyword": search_term,
                "cursor": cursor,
                "from_page": "search",
                "web_search_code": """{"tiktok":{"client_params_x":{"search_engine":{"ies_mt_user_live_video_card_use_libra":1,"mt_search_general_user_live_card":1}},"search_server":{}}}""",
                "search_id": ""
            }

            resp = await cls._parent.make_request(
                url=f"https://www.tiktok.com/api/search/{obj_type}/full/",
                params=params,
                headers=kwargs.get("headers"),
                session_index=kwargs.get("session_index"),
            )

            if resp is None:
                raise InvalidResponseException(
                    resp, "TikTok returned an invalid response."
                )

            if not params["search_id"]:
                params["search_id"] = resp.get("rid")

            if obj_type == "user":
                for user in resp.get("user_list", []):
                    sec_uid = user.get("user_info").get("sec_uid")
                    uid = user.get("user_info").get("user_id")
                    username = user.get("user_info").get("unique_id")
                    yield cls._parent.user(
                        sec_uid=sec_uid,
                        user_id=uid,
                        username=username
                    )
                    found += 1
            elif obj_type == "item":
                for video in resp.get("item_list", []):
                    yield cls._parent.video.from_raw_data(raw_data=video)

            if not resp.get("has_more", False):
                return

            cursor = resp.get("cursor")
