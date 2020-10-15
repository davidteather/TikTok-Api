from TikTokApi import TikTokApi


def test_trending():
    api = TikTokApi()
    assert abs(len(api.byUsername("therock", 5)) - 5) <= 2
    assert abs(len(api.byUsername("therock", 10)) - 10) <= 2
    assert abs(len(api.byUsername("therock", 20)) - 20) <= 2
