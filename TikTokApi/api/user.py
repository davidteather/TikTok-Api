from __future__ import annotations
from concurrent.futures import process

import json
import logging
import requests

from urllib.parse import quote, urlencode

from ..exceptions import *
from ..helpers import extract_tag_contents
from .search import Search

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ..tiktok import TikTokApi

class User():
    parent: TikTokApi

    def __init__(self, username: Optional[str] = None, user_id: Optional[str] = None, sec_uid: Optional[str] = None):
        self.username = username
        self.user_id = user_id
        self.sec_uid = sec_uid

    def user_object(self, **kwargs):
        return self.data_full(**kwargs)['UserModule']['users'][self.username]

    def data_full(self, **kwargs) -> dict:
        """Gets all data associated with the user."""

        # TODO: Find the one using only user_id & sec_uid
        if not self.username:
            raise TypeError('You must provide the username when creating this class to use this method.')

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

        if user["UserPage"]["statusCode"] == 404:
            raise TikTokNotFoundError("TikTok user with username {} does not exist".format(self.username))

        return user

    def videos(self, count=30, cursor=0, **kwargs) -> dict:
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
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                "count": realCount,
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
            for video in videos: yield video

            if not res.get("hasMore", False) and not first:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return

            realCount = count - amount_yielded
            cursor = res["cursor"]
            first = False

    def liked(self, count: int = 30, cursor: int = 0, **kwargs):
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
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        amount_yielded = 0
        first = True

        while amount_yielded < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                "count": realCount,
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
            api_url = "api/favorite/item_list/?{}&{}".format(
                User.parent.__add_url_params__(), urlencode(query)
            )

            res = self.get_data(url=api_url, **kwargs)

            if "itemList" not in res.keys():
                logging.error("User's likes are most likely private")
                return

            videos = res.get("itemList", [])
            amount_yielded += len(videos)
            for video in videos: yield video

            if not res.get("hasMore", False) and not first:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return

            realCount = count - amount_yielded
            cursor = res["cursor"]
            first = False

    def __find_attributes(self):
        # It is more efficient to check search first, since self.user_object() makes HTML request.
        user_object = None
        for r in Search(self.parent).users(self.username):
            if r['user_info']['unique_id'] == self.username:
                user_object = r['user_info']
                self.user_id = user_object['uid']
                self.sec_uid = user_object['sec_uid']
                self.username = user_object['unique_id']
                break

        if user_object is None:
            user_object = self.user_object()
            self.user_id = user_object['id']
            self.sec_uid = user_object['secUid']
            self.username = user_object['uniqueId']
