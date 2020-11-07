from TikTokApi import TikTokApi


def unique_count(tiktoks):
    tmp = []
    for t in tiktoks:
        if t["id"] not in tmp:
            tmp.append(t["id"])
    return tmp


def test_hashtag():
    api = TikTokApi()
    assert len(api.byHashtag("funny", 5)) == 5
    assert len(api.byHashtag("funny", 10)) == 10
    assert len(api.byHashtag("funny", 20)) == 20
    assert len(unique_count(api.byHashtag("funny", 500))) == 500


def test_non_latin1():
    api = TikTokApi()
    assert len(api.byHashtag("селфи", count=3)) == 3
