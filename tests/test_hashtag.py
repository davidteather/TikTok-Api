from TikTokApi import TikTokApi
import os

api = TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None))


def test_hashtag_videos():
    tag = api.hashtag(name="funny")
    video_count = 0
    for video in tag.videos(count=100):
        video_count += 1

    assert video_count >= 100


def test_hashtag_info():
    tag = api.hashtag(name="funny")
    data = tag.info()
    assert data["title"] == "funny"
    assert data["id"] == "5424"


def test_non_latin1():
    name = "селфи"
    tag = api.hashtag(name=name)
    data = tag.info()

    assert data["title"] == name
