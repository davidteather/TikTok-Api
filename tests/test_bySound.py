from TikTokApi import TikTokApi


def test_trending():
    api = TikTokApi()
    assert abs(len(api.bySound("6819262113299565318", 5)) - 5) <= 1
    assert abs(len(api.bySound("6819262113299565318", 10)) - 10) <= 1
    assert abs(len(api.bySound("6819262113299565318", 20)) - 20) <= 1
