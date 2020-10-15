from TikTokApi import TikTokApi


def test_trending():
    api = TikTokApi()
    assert len(api.discoverHashtags()) > 0
    assert len(api.discoverMusic()) > 0
