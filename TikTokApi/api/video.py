from __future__ import annotations
from ..helpers import extract_video_id_from_url, requests_cookie_to_playwright_cookie
from typing import TYPE_CHECKING, Any, ClassVar, AsyncIterator, Optional, Union
from datetime import datetime
import requests
from ..exceptions import InvalidResponseException
import json
import httpx

if TYPE_CHECKING:
    from ..tiktok import TikTokApi
    from .user import User
    from .sound import Sound
    from .hashtag import Hashtag
    from .comment import Comment


MediaBytes = Union[bytes, AsyncIterator[bytes]]


def _first_media_url(value: Any) -> Optional[str]:
    """Return the first HTTP URL from TikTok's nested media URL shapes."""
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        return value
    if isinstance(value, (list, tuple)):
        for item in value:
            if url := _first_media_url(item):
                return url
    if isinstance(value, dict):
        for key in (
            "urlList",
            "UrlList",
            "url_list",
            "downloadAddr",
            "playAddr",
            "PlayAddr",
            "url",
            "Url",
        ):
            if url := _first_media_url(value.get(key)):
                return url
    return None


def _video_info_from_html(html: str, video_id: Optional[str]) -> dict:
    """Extract a post object from either TikTok page hydration format."""
    sigi_marker = '<script id="SIGI_STATE" type="application/json">'
    start = html.find(sigi_marker)
    if start != -1:
        start += len(sigi_marker)
        end = html.find("</script>", start)
        if end != -1:
            items = json.loads(html[start:end]).get("ItemModule", {})
            if video_id and isinstance(items.get(video_id), dict):
                return items[video_id]
            for item in items.values():
                if isinstance(item, dict):
                    return item

    universal_marker = (
        '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" '
        'type="application/json">'
    )
    start = html.find(universal_marker)
    if start != -1:
        start += len(universal_marker)
        end = html.find("</script>", start)
        if end != -1:
            data = json.loads(html[start:end])
            detail = data.get("__DEFAULT_SCOPE__", {}).get("webapp.video-detail", {})
            if detail.get("statusCode", 0) == 0:
                item = detail.get("itemInfo", {}).get("itemStruct")
                if isinstance(item, dict):
                    return item

    raise ValueError("TikTok's page did not contain a recognizable post payload")


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
    media_type: Optional[str]
    """Either ``video`` or ``slideshow`` after post data has been loaded."""
    image_urls: list[str]
    """Original slideshow image URLs in display order."""
    video_url: Optional[str]
    """The preferred direct video URL, or ``None`` for a slideshow."""
    audio_url: Optional[str]
    """The direct music/audio URL when TikTok exposes one."""
    cover_url: Optional[str]
    """The first slideshow image or preferred video cover URL."""

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
                proxy=(
                    kwargs.get("proxy")
                    if kwargs.get("proxy") is not None
                    else session.proxy
                ),
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

        # TikTok serves hydration data more consistently from /video/ even for
        # photo posts. Keep self.url untouched, but normalize the request URL.
        request_url = self.url.replace("/photo/", "/video/", 1)
        r = requests.get(request_url, headers=session.headers, proxies=proxy)
        if r.status_code != 200:
            raise InvalidResponseException(
                r.text, "TikTok returned an invalid response.", error_code=r.status_code
            )

        try:
            video_info = _video_info_from_html(r.text, self.id)
        except (ValueError, KeyError, json.JSONDecodeError):
            # A browser-rendered retry handles TikTok's occasional JS challenge
            # without involving application-specific extractor code.
            try:
                await session.page.goto(request_url, wait_until="domcontentloaded")
                await session.page.wait_for_timeout(1500)
                video_info = _video_info_from_html(await session.page.content(), self.id)
            except Exception as exc:
                raise InvalidResponseException(
                    r.text,
                    "TikTok returned an invalid response structure.",
                    error_code=r.status_code,
                ) from exc

        self.as_dict = video_info
        self.__extract_from_data()

        cookies = [requests_cookie_to_playwright_cookie(c) for c in r.cookies]

        await self.parent.set_session_cookies(session, cookies)
        return video_info

    async def bytes(
        self, stream: bool = False, **kwargs
    ) -> MediaBytes:
        """
        Returns the bytes of a TikTok Video.

        Example Usage:
            .. code-block:: python

                video = api.video(
                    url='https://www.tiktok.com/@creator/video/7041997751718137094'
                )
                video_bytes = await video.bytes()

                # Saving The Video
                with open('saved_video.mp4', 'wb') as output:
                    output.write(video_bytes)

                # Streaming (if stream=True)
                stream = await video.bytes(stream=True)
                async for chunk in stream:
                    # Process or upload chunk
        """
        await self._ensure_info(**kwargs)
        if self.is_slideshow:
            raise TypeError(
                "This post is a slideshow. Use image_bytes() or images_bytes() instead."
            )
        if not self.video_url:
            raise InvalidResponseException(
                self.as_dict, "TikTok did not expose a downloadable video URL."
            )
        return await self._download_media(self.video_url, stream=stream, **kwargs)

    @property
    def is_slideshow(self) -> bool:
        """Whether the loaded post contains a TikTok photo slideshow."""
        return bool(getattr(self, "image_urls", []))

    @property
    def image_count(self) -> int:
        """Number of images in the loaded slideshow."""
        return len(getattr(self, "image_urls", []))

    async def image_bytes(
        self, index: int, stream: bool = False, **kwargs
    ) -> MediaBytes:
        """Return or stream one original slideshow image by zero-based index."""
        await self._ensure_info(**kwargs)
        if not self.is_slideshow:
            raise TypeError("This post is not a slideshow.")
        if not 0 <= index < len(self.image_urls):
            raise IndexError(
                f"Image index {index} is out of range for {len(self.image_urls)} images."
            )
        return await self._download_media(self.image_urls[index], stream=stream, **kwargs)

    async def images_bytes(self, **kwargs) -> list[bytes]:
        """Download every original slideshow image in display order."""
        await self._ensure_info(**kwargs)
        if not self.is_slideshow:
            raise TypeError("This post is not a slideshow.")
        output = []
        for image_url in self.image_urls:
            body = await self._download_media(image_url, stream=False, **kwargs)
            output.append(body)
        return output

    async def audio_bytes(
        self, stream: bool = False, **kwargs
    ) -> MediaBytes:
        """Return or stream the post's audio track."""
        await self._ensure_info(**kwargs)
        if not self.audio_url:
            raise InvalidResponseException(
                self.as_dict, "TikTok did not expose a downloadable audio URL."
            )
        return await self._download_media(self.audio_url, stream=stream, **kwargs)

    async def cover_bytes(
        self, stream: bool = False, **kwargs
    ) -> MediaBytes:
        """Return or stream the post's preferred cover image."""
        await self._ensure_info(**kwargs)
        if not self.cover_url:
            raise InvalidResponseException(
                self.as_dict, "TikTok did not expose a cover image URL."
            )
        return await self._download_media(self.cover_url, stream=stream, **kwargs)

    async def _ensure_info(self, **kwargs) -> None:
        if not hasattr(self, "as_dict"):
            await self.info(**kwargs)

    async def _download_media(
        self, url: str, stream: bool = False, **kwargs
    ) -> MediaBytes:
        _, session = self.parent._get_session(**kwargs)
        cookies = await self.parent.get_session_cookies(session)
        headers = dict(session.headers)
        headers.update(
            {
                "range": "bytes=0-",
                "accept-encoding": "identity;q=1, *;q=0",
                "referer": "https://www.tiktok.com/",
            }
        )

        if stream:
            async def stream_bytes():
                async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
                    async with client.stream(
                        "GET", url, headers=headers, cookies=cookies
                    ) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_bytes():
                            yield chunk

            return stream_bytes()

        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            response = await client.get(url, headers=headers, cookies=cookies)
            response.raise_for_status()
            return response.content

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
        self.stats = data.get("statsV2") or data.get("stats")

        author = data.get("author")
        if isinstance(author, str):
            self.author = self.parent.user(username=author)
        else:
            self.author = self.parent.user(data=author)
        self.sound = self.parent.sound(data=data)

        self.hashtags = [
            self.parent.hashtag(data=hashtag) for hashtag in data.get("challenges", [])
        ]

        self.image_urls = self._extract_image_urls(data)
        self.media_type = "slideshow" if self.image_urls else "video"
        self.video_url = None if self.image_urls else self._extract_video_url(data)
        self.audio_url = self._extract_audio_url(data)
        self.cover_url = self.image_urls[0] if self.image_urls else self._extract_cover_url(data)

        if getattr(self, "id", None) is None:
            Video.parent.logger.error(
                f"Failed to create Video with data: {data}\nwhich has keys {data.keys()}"
            )

    @staticmethod
    def _extract_image_urls(data: dict) -> list[str]:
        image_post = data.get("imagePost") or data.get("image_post") or {}
        urls = []
        for image in image_post.get("images", []):
            if not isinstance(image, dict):
                continue
            for key in (
                "imageURL",
                "imageUrl",
                "displayImage",
                "thumbnail",
                "ownerWatermarkImage",
            ):
                if url := _first_media_url(image.get(key)):
                    if url not in urls:
                        urls.append(url)
                    break
        return urls

    @staticmethod
    def _extract_video_url(data: dict) -> Optional[str]:
        video = data.get("video") or {}
        ranked_urls = []
        bitrate_info = video.get("bitrateInfo") or []
        if isinstance(bitrate_info, dict):
            bitrate_info = [bitrate_info]
        for item in bitrate_info:
            if not isinstance(item, dict):
                continue
            address = item.get("PlayAddr") or item.get("playAddr") or {}
            width = address.get("Width") or address.get("width") or 0
            height = address.get("Height") or address.get("height") or 0
            try:
                quality = int(width) * int(height)
            except (TypeError, ValueError):
                quality = 0
            if url := _first_media_url(address):
                ranked_urls.append((quality, url))
        if ranked_urls:
            return max(ranked_urls, key=lambda item: item[0])[1]
        for key in ("playAddr", "downloadAddr"):
            if url := _first_media_url(video.get(key)):
                return url
        return None

    @staticmethod
    def _extract_audio_url(data: dict) -> Optional[str]:
        music = data.get("music") or {}
        for key in ("playUrl", "play_url", "audioURL", "audioUrl"):
            if url := _first_media_url(music.get(key)):
                return url
        return None

    @staticmethod
    def _extract_cover_url(data: dict) -> Optional[str]:
        video = data.get("video") or {}
        for key in ("cover", "originCover", "dynamicCover"):
            if url := _first_media_url(video.get(key)):
                return url
        return None

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
