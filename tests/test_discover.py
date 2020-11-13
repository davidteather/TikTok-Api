from TikTokApi import TikTokApi
import os
api = TikTokApi.get_instance(proxy=os.environ.get("PROXY", None))


def test_trending():
    assert len(api.discoverHashtags()) > 0
    assert len(api.discoverMusic()) > 0
