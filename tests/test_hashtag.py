from TikTokApi import TikTokApi
import os


def test_hashtag_videos():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        tag = api.hashtag(name="funny")
        video_count = 0
        for video in tag.videos(count=100):
            video_count += 1

        assert video_count >= 100


def test_hashtag_info():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        tag = api.hashtag(name="funny")
        data = tag.info()
        assert data["title"] == "funny"
        assert data["id"] == "5424"


def test_non_latin1():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        name = "селфи"
        tag = api.hashtag(name=name)
        data = tag.info()

        assert data["title"] == name
