from __future__ import annotations

from typing import ClassVar, Optional
from typing import TYPE_CHECKING, ClassVar, Iterator, Optional

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .user import User


class Comment:
    """
    A TikTok Comment.

    Example Usage
    ```py
    for comment in video.comments:
        print(comment.text)
    ```
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
        self.id = self.as_dict["cid"]
        self.text = self.as_dict["text"]

        usr = self.as_dict["user"]
        self.author = self.parent.user(
            user_id=usr["uid"], username=usr["unique_id"], sec_uid=usr["sec_uid"]
        )
        self.likes_count = self.as_dict["digg_count"]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TikTokApi.comment(comment_id='{self.id}', text='{self.text}')"

    def __getattr__(self, name):
        if name in ["as_dict"]:
            self.as_dict = self.info()
            self.__extract_from_data()
            return self.__getattribute__(name)

        raise AttributeError(f"{name} doesn't exist on TikTokApi.api.Comment")
