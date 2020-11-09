from TikTokApi import TikTokApi
api = TikTokApi()

def test_trending():
    assert len(api.discoverHashtags()) > 0
    assert len(api.discoverMusic()) > 0
