from TikTokApi import TikTokApi
import os

api = TikTokApi.get_instance(
    custom_verifyFp=os.environ.get("verifyFp", None), use_test_endpoints=True
)


def test_tiktok_object():
    assert len(api.get_tiktok_by_id("6829267836783971589")) > 0
    assert (
        len(
            api.get_tiktok_by_url(
                "https://www.tiktok.com/@therock/video/6829267836783971589"
            )
        )
        > 0
    )


def test_user_object():
    assert len(api.get_user_object("therock")) > 0


def test_music_object():
    assert len(api.get_music_object("6820695018429253633")) > 0


def test_hashtag_object():
    assert len(api.get_hashtag_object("funny")) > 0
