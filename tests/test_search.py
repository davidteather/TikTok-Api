from TikTokApi import TikTokApi
import os


def test_video():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        count = 0
        for video in api.search.videos("therock", count=50):
            count += 1

        assert count >= 50


def test_users():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        count = 0
        found_ids = []
        for user in api.search.users("therock", count=50):
            if user.user_id in found_ids:
                raise Exception("Multiple Users on search.user")
            found_ids.append(user.user_id)
            count += 1

        assert count >= 50
