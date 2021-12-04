from TikTokApi import TikTokApi
import os

api = TikTokApi.get_instance(
    custom_verifyFp=os.environ.get("verifyFp", None), use_test_endpoints=True
)

device_id = api.generate_device_id()
trending = api.by_trending(custom_device_id=device_id)


def unique_count(tiktoks):
    tmp = []
    for t in tiktoks:
        if t["id"] not in tmp:
            tmp.append(t["id"])
    return tmp


def test_hashtag():
    assert len(api.by_hashtag("funny", 5)) == 5
    assert len(api.by_hashtag("funny", 50)) == 50


def test_non_latin1():
    assert len(api.by_hashtag("селфи", count=3)) == 3
