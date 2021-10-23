from TikTokApi import TikTokApi
import os

api = TikTokApi.get_instance(
    custom_verifyFp=os.environ.get(
        "verifyFp", None
    )  # use_test_endpoints=True - test endpoint not working on this endpoint anymore
)


def test_discover_trending():
    assert len(api.discover_hashtags()) > 0
    assert len(api.discover_music()) > 0
