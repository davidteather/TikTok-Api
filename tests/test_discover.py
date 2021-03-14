from TikTokApi import TikTokApi
import os

api = TikTokApi.get_instance(
    custom_verifyFp=os.environ.get("verifyFp", None), use_test_endpoints=True
)


def test_trending():
    assert len(api.discoverHashtags()) > 0
    assert len(api.discoverMusic()) > 0
