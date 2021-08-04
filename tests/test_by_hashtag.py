from TikTokApi import TikTokApi
import os

api = TikTokApi.get_instance(
    custom_verifyFp=os.environ.get("verifyFp", None), use_test_endpoints=True
)

device_id = api.generate_device_id()
trending = api.trending(custom_device_id=device_id)

# Below is if the method used if you have the full tiktok object
video_bytes = api.get_Video_By_TikTok(trending[0], custom_device_id=device_id)

with open("video.mp4", "wb") as out:
    out.write(video_bytes)


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
