from TikTokApi import TikTokApi
import os

username = "charlidamelio"
user_id = "5831967"
sec_uid = "MS4wLjABAAAA-VASjiXTh7wDDyXvjk10VFhMWUAoxr8bgfO1kAL1-9s"


def test_user_info():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        data = api.user(username=username).info()

        assert data["uniqueId"] == username
        assert data["id"] == user_id
        assert data["secUid"] == sec_uid


def test_user_videos():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        count = 0
        for video in api.user(username=username).videos(count=100):
            count += 1

        assert count >= 100

        count = 0
        for video in api.user(user_id=user_id, sec_uid=sec_uid).videos(count=100):
            count += 1

        assert count >= 100


def test_user_liked():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        user = api.user(username="public_likes")

        count = 0
        for v in user.liked():
            count += 1

        assert count >= 1
