from TikTokApi import TikTokApi
import os
api = TikTokApi.get_instance(proxy=os.environ.get("PROXY", None))


def test_search_for():
    assert len(api.search_for_hashtags("a")) >= 20
    assert len(api.search_for_music("a")) >= 20
    assert len(api.search_for_users("a")) >= 20
