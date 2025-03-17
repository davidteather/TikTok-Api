from __future__ import annotations
from ..helpers import extract_video_id_from_url, requests_cookie_to_playwright_cookie
from typing import TYPE_CHECKING, ClassVar, AsyncIterator, Optional
from datetime import datetime
import requests
from ..exceptions import InvalidResponseException
import json
import httpx
from typing import Union, AsyncIterator

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .user import User
    from .sound import Sound
    from .hashtag import Hashtag
    from .comment import Comment


class Video:
    """
    A TikTok Video class

    Example Usage
    ```py
    video = api.video(id='7041997751718137094')
    ```
    """

    parent: ClassVar[TikTokApi]

    id: Optional[str]
    """TikTok's ID of the Video"""
    url: Optional[str]
    """The URL of the Video"""
    create_time: Optional[datetime]
    """The creation time of the Video"""
    stats: Optional[dict]
    """TikTok's stats of the Video"""
    author: Optional[User]
    """The User who created the Video"""
    sound: Optional[Sound]
    """The Sound that is associated with the Video"""
    hashtags: Optional[list[Hashtag]]
    """A List of Hashtags on the Video"""
    as_dict: dict
    """The raw data associated with this Video."""

    def __init__(
        self,
        id: Optional[str] = None,
        url: Optional[str] = None,
        data: Optional[dict] = None,
        **kwargs,
    ):
        """
        You must provide the id or a valid url, else this will fail.
        """
        self.id = id
        self.url = url
        if data is not None:
            self.as_dict = data
            self.__extract_from_data()
        elif url is not None:
            i, session = self.parent._get_session(**kwargs)
            self.id = extract_video_id_from_url(
                url,
                headers=session.headers,
                proxy=kwargs.get("proxy")
                if kwargs.get("proxy") is not None
                else session.proxy,
            )

        if getattr(self, "id", None) is None:
            raise TypeError("You must provide id or url parameter.")

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
        i, session = self.parent._get_session(**kwargs)
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
                    r.text, "TikTok returned an invalid response.", error_code=r.status_code
                )

            data = json.loads(r.text[start:end])
            video_info = data["ItemModule"][self.id]
        else:
            # Try __UNIVERSAL_DATA_FOR_REHYDRATION__ next

            # extract tag <script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">{..}</script>
            # extract json in the middle

            start = r.text.find('<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">')
            if start == -1:
                raise InvalidResponseException(
                    r.text, "TikTok returned an invalid response.", error_code=r.status_code
                )

            start += len('<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">')
            end = r.text.find("</script>", start)

            if end == -1:
                raise InvalidResponseException(
                    r.text, "TikTok returned an invalid response.", error_code=r.status_code
                )

            data = json.loads(r.text[start:end])
            default_scope = data.get("__DEFAULT_SCOPE__", {})
            video_detail = default_scope.get("webapp.video-detail", {})
            if video_detail.get("statusCode", 0) != 0: # assume 0 if not present
                raise InvalidResponseException(
                    r.text, "TikTok returned an invalid response structure.", error_code=r.status_code
                )
            video_info = video_detail.get("itemInfo", {}).get("itemStruct")
            if video_info is None:
                raise InvalidResponseException(
                    r.text, "TikTok returned an invalid response structure.", error_code=r.status_code
                )

        self.as_dict = video_info
        self.__extract_from_data()

        cookies = [requests_cookie_to_playwright_cookie(c) for c in r.cookies]

        await self.parent.set_session_cookies(
            session,
            cookies
        )
        return video_info

    async def bytes(self, stream: bool = False, **kwargs) -> Union[bytes, AsyncIterator[bytes]]:
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
        i, session = self.parent._get_session(**kwargs)
        downloadAddr = self.as_dict["video"]["downloadAddr"]

        cookies = await self.parent.get_session_cookies(session)

        h = session.headers
        h["range"] = 'bytes=0-'
        h["accept-encoding"] = 'identity;q=1, *;q=0'
        h["referer"] = 'https://www.tiktok.com/'

        if stream:
            async def stream_bytes():
                async with httpx.AsyncClient() as client:
                    async with client.stream('GET', downloadAddr, headers=h, cookies=cookies) as response:
                        async for chunk in response.aiter_bytes():
                            yield chunk
            return stream_bytes()
        else:
            resp = requests.get(downloadAddr, headers=h, cookies=cookies)
            return resp.content

    def __extract_from_data(self) -> None:
        data = self.as_dict
        self.id = data["id"]

        timestamp = data.get("createTime", None)
        if timestamp is not None:
            try:
                timestamp = int(timestamp)
            except ValueError:
                pass

        self.create_time = datetime.fromtimestamp(timestamp)
        self.stats = data.get('statsV2') or data.get('stats')

        author = data.get("author")
        if isinstance(author, str):
            self.author = self.parent.user(username=author)
        else:
            self.author = self.parent.user(data=author)
        self.sound = self.parent.sound(data=data)

        self.hashtags = [
            self.parent.hashtag(data=hashtag) for hashtag in data.get("challenges", [])
        ]

        if getattr(self, "id", None) is None:
            Video.parent.logger.error(
                f"Failed to create Video with data: {data}\nwhich has keys {data.keys()}"
            )

    async def comments(self, count=20, cursor=0, **kwargs) -> AsyncIterator[Comment]:
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

            resp = await self.parent.make_request(
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
                yield self.parent.comment(data=video)
                found += 1

            if not resp.get("has_more", False):
                return

            cursor = resp.get("cursor")

    async def related_videos(
        self, count: int = 30, cursor: int = 0, **kwargs
    ) -> AsyncIterator[Video]:
        """
        Returns related videos of a TikTok Video.

        Parameters:
            count (int): The amount of comments you want returned.
            cursor (int): The the offset of comments from 0 you want to get.

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

            resp = await self.parent.make_request(
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
                yield self.parent.video(data=video)
                found += 1

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TikTokApi.video(id='{getattr(self, 'id', None)}')"
