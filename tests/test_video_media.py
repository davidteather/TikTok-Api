import pytest

from TikTokApi import TikTokApi
from TikTokApi.helpers import extract_video_id_from_url


SLIDESHOW_DATA = {
    "id": "7646577917811625237",
    "createTime": "1784646000",
    "author": {
        "id": "1001",
        "secUid": "test-sec-uid",
        "uniqueId": "mangaodyssey",
        "nickname": "Manga Odyssey",
    },
    "music": {"playUrl": "https://media.example/audio.mp3"},
    "imagePost": {
        "images": [
            {
                "imageURL": {
                    "urlList": [
                        "https://media.example/image-1.jpg",
                        "https://media.example/image-1-backup.jpg",
                    ]
                },
                "imageWidth": 1080,
                "imageHeight": 1440,
            },
            {
                "displayImage": {
                    "urlList": ["https://media.example/image-2.jpg"]
                },
                "imageWidth": 1080,
                "imageHeight": 1440,
            },
        ]
    },
    "stats": {},
}


def test_photo_url_id_is_supported(monkeypatch):
    class Response:
        url = "https://www.tiktok.com/@mangaodyssey/photo/7646577917811625237?q=test"

    monkeypatch.setattr("TikTokApi.helpers.requests.head", lambda **kwargs: Response())

    assert extract_video_id_from_url(Response.url) == "7646577917811625237"


def test_slideshow_media_is_extracted_in_order():
    api = TikTokApi()
    post = api.video(data=SLIDESHOW_DATA)

    assert post.is_slideshow is True
    assert post.media_type == "slideshow"
    assert post.image_count == 2
    assert post.image_urls == [
        "https://media.example/image-1.jpg",
        "https://media.example/image-2.jpg",
    ]
    assert post.video_url is None
    assert post.audio_url == "https://media.example/audio.mp3"
    assert post.cover_url == post.image_urls[0]


@pytest.mark.asyncio
async def test_image_and_audio_byte_helpers(monkeypatch):
    api = TikTokApi()
    post = api.video(data=SLIDESHOW_DATA)
    requested = []

    async def fake_download(url, stream=False, **kwargs):
        requested.append((url, stream))
        return url.encode()

    monkeypatch.setattr(post, "_download_media", fake_download)

    assert await post.image_bytes(1) == b"https://media.example/image-2.jpg"
    assert await post.images_bytes() == [
        b"https://media.example/image-1.jpg",
        b"https://media.example/image-2.jpg",
    ]
    assert await post.audio_bytes() == b"https://media.example/audio.mp3"
    assert requested == [
        ("https://media.example/image-2.jpg", False),
        ("https://media.example/image-1.jpg", False),
        ("https://media.example/image-2.jpg", False),
        ("https://media.example/audio.mp3", False),
    ]


@pytest.mark.asyncio
async def test_video_bytes_rejects_slideshows():
    api = TikTokApi()
    post = api.video(data=SLIDESHOW_DATA)

    with pytest.raises(TypeError, match="slideshow"):
        await post.bytes()


def test_regular_video_prefers_highest_resolution_bitrate():
    data = {
        "id": "1",
        "createTime": "1784646000",
        "author": {"id": "1002", "secUid": "test-sec-uid", "uniqueId": "tester"},
        "stats": {},
        "video": {
            "bitrateInfo": [
                {"PlayAddr": {"Width": 540, "Height": 960, "UrlList": ["https://media.example/low.mp4"]}},
                {"PlayAddr": {"Width": 1080, "Height": 1920, "UrlList": ["https://media.example/high.mp4"]}},
            ],
            "cover": "https://media.example/cover.jpg",
        },
    }
    post = TikTokApi().video(data=data)

    assert post.is_slideshow is False
    assert post.media_type == "video"
    assert post.video_url == "https://media.example/high.mp4"
    assert post.cover_url == "https://media.example/cover.jpg"
