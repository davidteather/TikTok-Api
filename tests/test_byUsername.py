from TikTokApi import TikTokApi

def test_trending():
    api = TikTokApi()
    assert abs(len(api.byHashtag('independent', 5))-5) <= 1
    assert abs(len(api.byHashtag('independent', 10))-10) <= 1
    assert abs(len(api.byHashtag('independent', 20))-20) <= 1