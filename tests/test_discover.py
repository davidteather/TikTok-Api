from TikTokApi import TikTokApi
import os

api = TikTokApi.get_instance(
    custom_verifyFp=os.environ.get("verifyFp", None), use_test_endpoints=True
)


def test_discover_trending():
    assert len(api.discover_hashtags()) > 0
    assert len(api.discover_music()) > 0
