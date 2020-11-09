from TikTokApi import TikTokApi


def test_trending():
    api = TikTokApi()
    assert abs(len(api.trending(5)) - 5) <= 2
    assert abs(len(api.trending(10)) - 10) <= 2
    assert abs(len(api.trending(20)) - 20) <= 2
