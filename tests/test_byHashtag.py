from TikTokApi import TikTokApi
import os

api = TikTokApi.get_instance(
    custom_verifyFp=os.environ.get("verifyFp", None), use_test_endpoints=True
)


def unique_count(tiktoks):
    tmp = []
    for t in tiktoks:
        if t["id"] not in tmp:
            tmp.append(t["id"])
    return tmp


def test_hashtag():
    assert len(api.byHashtag("funny", 5)) == 5
    assert len(api.byHashtag("funny", 10)) == 10
    assert len(api.byHashtag("funny", 20)) == 20
    # Grant A Little Lenience of at most a 15 difference
    assert abs(len(unique_count(api.byHashtag("funny", 500))) - 500) <= 15


def test_non_latin1():
    assert len(api.byHashtag("селфи", count=3)) == 3
