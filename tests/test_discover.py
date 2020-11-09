from TikTokApi import TikTokApi

api = TikTokApi.get_instance()


def test_trending():
    assert len(api.discoverHashtags()) > 0
    assert len(api.discoverMusic()) > 0
