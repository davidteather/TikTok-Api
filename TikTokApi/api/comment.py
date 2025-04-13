from __future__ import annotations

from typing import ClassVar, AsyncIterator, Optional
from typing import TYPE_CHECKING, ClassVar, Optional

from TikTokApi.exceptions import InvalidResponseException

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .user import User


class Comment:
    """
    A TikTok Comment.

    Example Usage
        .. code-block:: python

            for comment in video.comments:
                print(comment.text)
                print(comment.as_dict)
    """

    parent: ClassVar[TikTokApi]

    id: str
    """The id of the comment"""
    author: ClassVar[User]
    """The author of the comment"""
    text: str
    """The contents of the comment"""
    likes_count: int
    """The amount of likes of the comment"""
    as_dict: dict
    """The raw data associated with this comment"""

    def __init__(self, data: Optional[dict] = None):
        if data is not None:
            self.as_dict = data
            self.__extract_from_data()

    def __extract_from_data(self):
        data = self.as_dict
        self.id = self.as_dict["cid"]
        self.text = self.as_dict["text"]

        usr = self.as_dict["user"]
        self.author = self.parent.user(
            user_id=usr["uid"], username=usr["unique_id"], sec_uid=usr["sec_uid"]
        )
        self.likes_count = self.as_dict["digg_count"]

    async def replies(self, count=20, cursor=0, **kwargs) -> AsyncIterator[Comment]:
        found = 0

        while found < count:
            params = {
                "count": 20,
                "cursor": cursor,
                "item_id": self.author.user_id,
                "comment_id": self.id,
            }

            resp = await self.parent.make_request(
                url="https://www.tiktok.com/api/comment/list/reply/",
                params=params,
                headers=kwargs.get("headers"),
                session_index=kwargs.get("session_index"),
            )

            if resp is None:
                raise InvalidResponseException(
                    resp, "TikTok returned an invalid response."
                )

            for comment in resp.get("comments", []):
                yield self.parent.comment(data=comment)
                found += 1

            if not resp.get("has_more", False):
                return

            cursor = resp.get("cursor")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        id = getattr(self, "id", None)
        text = getattr(self, "text", None)
        return f"TikTokApi.comment(comment_id='{id}', text='{text}')"
