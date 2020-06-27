from TikTokApi import TikTokApi

def test_trending():
    api = TikTokApi()
    assert abs(len(api.byUsername('independent', 5))-5) <= 1
    assert abs(len(api.byUsername('independent', 10))-10) <= 1
    assert abs(len(api.byUsername('independent', 20))-20) <= 1