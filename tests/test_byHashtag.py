from TikTokApi import TikTokApi


def test_hashtag():
    api = TikTokApi()
    assert abs(len(api.byHashtag("funny", 5)) - 5) <= 1
    assert abs(len(api.byHashtag("funny", 10)) - 10) <= 1
    assert abs(len(api.byHashtag("funny", 20)) - 20) <= 1


def test_non_latin1():
    api = TikTokApi()

    assert len(api.byHashtag("селфи", count=3)) == 3
