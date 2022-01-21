from __future__ import annotations

from urllib.parse import urlencode

from ..helpers import extract_video_id_from_url

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ..tiktok import TikTokApi

class Video():
    parent: TikTokApi

    def __init__(self, id: Optional[str] = None, url: Optional[str] = None, raw: Optional[dict] = None):
        if id:
            self.id = id
        elif url:
            self.id = extract_video_id_from_url(url)
        else:
            raise TypeError("You must provide id or url parameter.")

    def video_info(self, **kwargs) -> dict:
        return self.data_full(**kwargs)['itemInfo']['itemStruct']

    def data_full(self, **kwargs) -> dict:
        """Returns a dictionary of a specific TikTok."""
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        device_id = kwargs.get("custom_device_id", None)
        query = {
            "itemId": self.id,
        }
        path = "api/item/detail/?{}&{}".format(
            self.parent._add_url_params(), urlencode(query)
        )

        return self.parent.get_data(path, **kwargs)

    def bytes(self, **kwargs) -> bytes:
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self.parent._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        video_data = self.video_info(**kwargs)
        download_url = video_data['video']['playAddr']

        return self.parent.get_bytes(url=download_url, **kwargs)