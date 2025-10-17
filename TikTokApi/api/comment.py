from __future__ import annotations

from typing import AsyncIterator, TYPE_CHECKING

from TikTokApi.exceptions import InvalidResponseException
from TikTokApi.tiktok_model import TikTokModel

if TYPE_CHECKING:
    from .user import User


class Comment(TikTokModel):
    """
    A TikTok Comment.

    Example Usage
        .. code-block:: python

            for comment in video.comments:
                print(comment.text)
                print(comment.as_dict)
    """

    id: str | None = None
    """The id of the comment"""

    author: User | None = None
    """The author of the comment"""

    text: str | None = None
    """The contents of the comment"""

    likes_count: int | None = None
    """The amount of likes of the comment"""

    def _extract_from_data(self, raw_data: dict):
        self.raw_data = raw_data
        self.id = self.raw_data["cid"]
        self.text = self.raw_data["text"]

        # Extract from user
        user = self.raw_data["user"]

        self.author = self._parent.user(
            user_id=user["uid"],
            username=user["unique_id"],
            sec_uid=user["sec_uid"]
        )

        self.likes_count = self.raw_data["digg_count"]

    async def replies(self, count: int = 20, cursor: int = 0, **kwargs) -> AsyncIterator["Comment"]:
        found = 0

        while found < count:
            params = {
                "count": 20,
                "cursor": cursor,
                "item_id": self.author.user_id,
                "comment_id": self.id,
            }

            resp = await self._parent.make_request(
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
                yield self._parent.comment.from_raw_data(raw_data=comment)
                found += 1

            if not resp.get("has_more", False):
                return

            cursor = resp.get("cursor")
