from __future__ import annotations

import json
from datetime import datetime
from typing import Union, AsyncIterator, TYPE_CHECKING

import httpx
import requests

from ..exceptions import InvalidResponseException
from ..helpers import requests_cookie_to_playwright_cookie
from TikTokApi.tiktok_model import TikTokModel

if TYPE_CHECKING:
    from .comment import Comment
    from .hashtag import Hashtag
    from .sound import Sound
    from .user import User


class Video(TikTokModel):
    """
    A TikTok Video class

    Example Usage
    ```py
    video = api.video(id='7041997751718137094')
    ```
    """

    id: str | None = None
    """TikTok's ID of the Video"""

    url: str | None = None
    """The URL of the Video"""

    create_time: datetime | None = None
    """The creation time of the Video"""

    stats: dict | None = None
    """TikTok's stats of the Video"""

    author: User | None = None
    """The User who created the Video"""

    sound: Sound | None = None
    """The Sound that is associated with the Video"""

    hashtags: list[Hashtag] = []
    """A List of Hashtags on the Video"""

    def __init__(self, **kwargs):

        if kwargs.get('url') and not kwargs.get('id'):
            kwargs['id'] = self._extract_id_from_url(kwargs['url'])

        super().__init__(**kwargs)

    @classmethod
    def _extract_id_from_url(cls, url: str) -> str | None:
        if "@" in url and "/video/" in url:
            return url.split("/video/")[1].split("?")[0]
        return None

    @classmethod
    async def from_url(cls, url: str, **kwargs) -> Video:
        """
        Creates a Video object from a TikTok URL.

        Parameters:
            url (str): The URL of the TikTok video.
        Returns:
            Video: An instance of the Video class.
        Raises:
            TypeError: If the URL format is not supported.

        """

        session = await cls._parent.get_random_session(**kwargs)

        response: httpx.Response = httpx.head(
            url=url,
            follow_redirects=True,
            headers=kwargs.get("headers") or session.headers,
            proxy=kwargs.get("proxy", None) or session.proxy,
        )

        final_url = str(response.url)
        video_id = cls._extract_id_from_url(final_url)

        if not video_id:
            raise TypeError(
                "URL format not supported. Below is an example of a supported url.\n"
                "https://www.tiktok.com/@therock/video/6829267836783971589"
            )

        return cls(id=video_id, url=final_url, **kwargs)

    async def info(self, **kwargs) -> dict:
        """
        Returns a dictionary of all data associated with a TikTok Video.

        Note: This is slow since it requires an HTTP request, avoid using this if possible.

        Returns:
            dict: A dictionary of all data associated with a TikTok Video.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                url = "https://www.tiktok.com/@davidteathercodes/video/7106686413101468970"
                video_info = await api.video(url=url).info()
        """
        session = await self._parent.get_random_session(**kwargs)
        proxy = (
            kwargs.get("proxy") if kwargs.get("proxy") is not None else session.proxy
        )
        if self.url is None:
            raise TypeError("To call video.info() you need to set the video's url.")

        r = requests.get(self.url, headers=session.headers, proxies=proxy)
        if r.status_code != 200:
            raise InvalidResponseException(
                r.text, "TikTok returned an invalid response.", error_code=r.status_code
            )

        # Try SIGI_STATE first
        # extract tag <script id="SIGI_STATE" type="application/json">{..}</script>
        # extract json in the middle

        start = r.text.find('<script id="SIGI_STATE" type="application/json">')
        if start != -1:
            start += len('<script id="SIGI_STATE" type="application/json">')
            end = r.text.find("</script>", start)

            if end == -1:
                raise InvalidResponseException(
                    r.text,
                    "TikTok returned an invalid response.",
                    error_code=r.status_code,
                )

            data = json.loads(r.text[start:end])
            video_info = data["ItemModule"][self.id]
        else:
            # Try __UNIVERSAL_DATA_FOR_REHYDRATION__ next

            # extract tag <script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">{..}</script>
            # extract json in the middle

            start = r.text.find(
                '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
            )
            if start == -1:
                raise InvalidResponseException(
                    r.text,
                    "TikTok returned an invalid response.",
                    error_code=r.status_code,
                )

            start += len(
                '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
            )
            end = r.text.find("</script>", start)

            if end == -1:
                raise InvalidResponseException(
                    r.text,
                    "TikTok returned an invalid response.",
                    error_code=r.status_code,
                )

            data = json.loads(r.text[start:end])
            default_scope = data.get("__DEFAULT_SCOPE__", {})
            video_detail = default_scope.get("webapp.video-detail", {})
            if video_detail.get("statusCode", 0) != 0:  # assume 0 if not present
                raise InvalidResponseException(
                    r.text,
                    "TikTok returned an invalid response structure.",
                    error_code=r.status_code,
                )
            video_info = video_detail.get("itemInfo", {}).get("itemStruct")
            if video_info is None:
                raise InvalidResponseException(
                    r.text,
                    "TikTok returned an invalid response structure.",
                    error_code=r.status_code,
                )

        self._extract_from_data(video_info)
        cookies = [requests_cookie_to_playwright_cookie(c) for c in r.cookies]
        await self._parent.set_session_cookies(session, cookies)
        return video_info

    async def bytes(
            self, stream: bool = False, **kwargs
    ) -> Union[bytes, AsyncIterator[bytes]]:
        """
        Returns the bytes of a TikTok Video.

        TODO:
            Not implemented yet.

        Example Usage:
            .. code-block:: python

                video_bytes = await api.video(id='7041997751718137094').bytes()

                # Saving The Video
                with open('saved_video.mp4', 'wb') as output:
                    output.write(video_bytes)

                # Streaming (if stream=True)
                async for chunk in api.video(id='7041997751718137094').bytes(stream=True):
                    # Process or upload chunk
        """
        i, session = self._parent._get_session(**kwargs)
        downloadAddr = self.raw_data["video"]["downloadAddr"]

        cookies = await self._parent.get_session_cookies(session)

        h = session.headers
        h["range"] = "bytes=0-"
        h["accept-encoding"] = "identity;q=1, *;q=0"
        h["referer"] = "https://www.tiktok.com/"

        if stream:

            async def stream_bytes():
                async with httpx.AsyncClient() as client:
                    async with client.stream(
                            "GET", downloadAddr, headers=h, cookies=cookies
                    ) as response:
                        async for chunk in response.aiter_bytes():
                            yield chunk

            return stream_bytes()
        else:
            resp = requests.get(downloadAddr, headers=h, cookies=cookies)
            return resp.content

    def _extract_from_data(self, raw_data: dict) -> None:
        self.raw_data = raw_data
        self.id = raw_data["id"]

        timestamp: int | None = raw_data.get("createTime", None)
        if timestamp is not None:
            try:
                timestamp = int(timestamp)
            except ValueError:
                pass

        self.create_time = datetime.fromtimestamp(timestamp)
        self.stats = raw_data.get("statsV2") or raw_data.get("stats")

        author = raw_data.get("author")
        if isinstance(author, str):
            self.author = self._parent.user(username=author)
        else:
            self.author = self._parent.user.from_raw_data(raw_data=author)
        self.sound = self._parent.sound.from_raw_data(raw_data=raw_data)

        self.hashtags = [
            self._parent.hashtag.from_raw_data(raw_data=hashtag) for hashtag in raw_data.get("challenges", [])
        ]

        if getattr(self, "id", None) is None:
            self._parent.logger.error(
                f"Failed to create Video with data: {raw_data}\nwhich has keys {raw_data.keys()}"
            )

    async def comments(self, count=20, cursor=0, **kwargs) -> AsyncIterator["Comment"]:
        """
        Returns the comments of a TikTok Video.

        Parameters:
            count (int): The amount of comments you want returned.
            cursor (int): The the offset of comments from 0 you want to get.

        Returns:
            async iterator/generator: Yields TikTokApi.comment objects.

        Example Usage
        .. code-block:: python

            async for comment in api.video(id='7041997751718137094').comments():
                # do something
        ```
        """
        found = 0
        while found < count:
            params = {
                "aweme_id": self.id,
                "count": 20,
                "cursor": cursor,
            }

            resp = await self._parent.make_request(
                url="https://www.tiktok.com/api/comment/list/",
                params=params,
                headers=kwargs.get("headers"),
                session_index=kwargs.get("session_index"),
            )

            if resp is None:
                raise InvalidResponseException(
                    resp, "TikTok returned an invalid response."
                )

            for video in resp.get("comments", []):
                yield self._parent.comment.from_raw_data(raw_data=video)
                found += 1

            if not resp.get("has_more", False):
                return

            cursor = resp.get("cursor")

    async def related_videos(self, count: int = 30, **kwargs) -> AsyncIterator[Video]:
        """
        Returns related videos of a TikTok Video.

        Parameters:
            count (int): The amount of comments you want returned.

        Returns:
            async iterator/generator: Yields TikTokApi.video objects.

        Example Usage
        .. code-block:: python

            async for related_videos in api.video(id='7041997751718137094').related_videos():
                # do something
        ```
        """
        found = 0
        while found < count:
            params = {
                "itemID": self.id,
                "count": 16,
            }

            resp = await self._parent.make_request(
                url="https://www.tiktok.com/api/related/item_list/",
                params=params,
                headers=kwargs.get("headers"),
                session_index=kwargs.get("session_index"),
            )

            if resp is None:
                raise InvalidResponseException(
                    resp, "TikTok returned an invalid response."
                )

            for video in resp.get("itemList", []):
                yield self._parent.video.from_raw_data(video)
                found += 1
