from TikTokApi import TikTokApi

def test_trending():
    api = TikTokApi()
    assert len(api.trending(5)) == 5
    assert len(api.trending(10)) == 10
    assert len(api.trending(20)) == 20