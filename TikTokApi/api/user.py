from __future__ import annotations

import json
import logging
import requests

from urllib.parse import quote, urlencode

from ..exceptions import *
from ..helpers import extract_tag_contents

from typing import TYPE_CHECKING, ClassVar, Generator, Optional

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .video import Video


class User:
    """A TikTok User class

    Attributes
        user_id: The TikTok user's ID.
        sec_uid: The TikTok user's sec_uid.
        username: The TikTok user's username.
        as_dict: The dictionary provided to create the class.
    """

    parent: ClassVar[TikTokApi]

    user_id: str
    sec_uid: str
    username: str
    as_dict: dict

    def __init__(
        self,
        username: Optional[str] = None,
        user_id: Optional[str] = None,
        sec_uid: Optional[str] = None,
        data: Optional[str] = None,
    ):
        self.__update_id_sec_uid_username(user_id, sec_uid, username)
        if data is not None:
            self.as_dict = data
            self.__extract_from_data()

    def info(self, **kwargs):
        # TODO: Might throw a key error with the HTML
        return self.info_full(**kwargs)["props"]["pageProps"]["userInfo"]["user"]

    def info_full(self, **kwargs) -> dict:
        """Gets all data associated with the user."""

        # TODO: Find the one using only user_id & sec_uid
        if not self.username:
            raise TypeError(
                "You must provide the username when creating this class to use this method."
            )

        quoted_username = quote(self.username)
        r = requests.get(
            "https://tiktok.com/@{}?lang=en".format(quoted_username),
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "path": "/@{}".format(quoted_username),
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "User-Agent": self.parent.user_agent,
            },
            proxies=User.parent._format_proxy(kwargs.get("proxy", None)),
            cookies=User.parent.get_cookies(**kwargs),
            **User.parent.requests_extra_kwargs,
        )

        data = extract_tag_contents(r.text)
        user = json.loads(data)

        if user["props"]["pageProps"]["statusCode"] == 404:
            raise TikTokNotFoundError(
                "TikTok user with username {} does not exist".format(self.username)
            )

        return user

    def videos(self, count=30, cursor=0, **kwargs) -> Generator[Video, None, None]:
        """Returns an array of dictionaries representing TikToks for a user.

        ##### Parameters
        * count: The number of posts to return

            Note: seems to only support up to ~2,000
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = User.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        if not self.user_id and not self.sec_uid:
            self.__find_attributes()

        first = True
        amount_yielded = 0

        while amount_yielded < count:
            query = {
                "count": 30,
                "id": self.user_id,
                "cursor": cursor,
                "type": 1,
                "secUid": self.sec_uid,
                "sourceType": 8,
                "appId": 1233,
                "region": region,
                "priority_region": region,
                "language": language,
            }
            path = "api/post/item_list/?{}&{}".format(
                User.parent._add_url_params(), urlencode(query)
            )

            res = User.parent.get_data(path, send_tt_params=True, **kwargs)

            videos = res.get("itemList", [])
            amount_yielded += len(videos)
            for video in videos:
                yield self.parent.video(data=video)

            if not res.get("hasMore", False) and not first:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return

            cursor = res["cursor"]
            first = False

    def liked(
        self, count: int = 30, cursor: int = 0, **kwargs
    ) -> Generator[Video, None, None]:
        """Returns a dictionary listing TikToks that a given a user has liked.
            Note: The user's likes must be public

        ##### Parameters
        * count: The number of posts to return

            Note: seems to only support up to ~2,000
        * cursor: The offset of a page

            The offset to return new videos from
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        amount_yielded = 0
        first = True

        if self.user_id is None and self.sec_uid is None:
            self.__find_attributes()

        while amount_yielded < count:
            query = {
                "count": 30,
                "id": self.user_id,
                "type": 2,
                "secUid": self.sec_uid,
                "cursor": cursor,
                "sourceType": 9,
                "appId": 1233,
                "region": region,
                "priority_region": region,
                "language": language,
            }
            path = "api/favorite/item_list/?{}&{}".format(
                User.parent._add_url_params(), urlencode(query)
            )

            res = self.parent.get_data(path, **kwargs)

            if "itemList" not in res.keys():
                logging.error("User's likes are most likely private")
                return

            videos = res.get("itemList", [])
            amount_yielded += len(videos)
            for video in videos:
                amount_yielded += 1
                yield self.parent.video(data=video)

            if not res.get("hasMore", False) and not first:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return

            cursor = res["cursor"]
            first = False

    def __extract_from_data(self):
        data = self.as_dict
        keys = data.keys()

        if "user_info" in keys:
            self.__update_id_sec_uid_username(
                data["user_info"]["uid"],
                data["user_info"]["sec_uid"],
                data["user_info"]["unique_id"],
            )
        elif "uniqueId" in keys:
            self.__update_id_sec_uid_username(
                data["id"], data["secUid"], data["uniqueId"]
            )

        if None in (self.username, self.user_id, self.sec_uid):
            logging.error(
                f"Failed to create User with data: {data}\nwhich has keys {data.keys()}"
            )

    def __update_id_sec_uid_username(self, id, sec_uid, username):
        self.user_id = id
        self.sec_uid = sec_uid
        self.username = username

    def __find_attributes(self) -> None:
        # It is more efficient to check search first, since self.user_object() makes HTML request.
        found = False
        for u in self.parent.search.users(self.username):
            if u.username == self.username:
                found = True
                self.__update_id_sec_uid_username(u.user_id, u.sec_uid, u.username)
                break

        if not found:
            user_object = self.info()
            self.__update_id_sec_uid_username(
                user_object["id"], user_object["secUid"], user_object["uniqueId"]
            )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TikTokApi.user(username='{self.username}', user_id='{self.user_id}', sec_uid='{self.sec_uid}')"

    def __getattr__(self, name):
        if name in ["as_dict"]:
            self.as_dict = self.info()
            self.__extract_from_data()
            return self.__getattribute__(name)

        raise AttributeError(f"{name} doesn't exist on TikTokApi.api.User")
