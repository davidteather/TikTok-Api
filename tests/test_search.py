from TikTokApi import TikTokApi
import os

api = TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None))


def test_discover_type():
    count = 0
    found_ids = []
    for result in api.search.users("therock", count=50):
        if result.user_id in found_ids:
            raise Exception("Multiple Users on search.user")
        found_ids.append(result.user_id)
        count += 1

    assert count >= 50

    count = 0
    found_ids
    for result in api.search.sounds("funny", count=50):
        if result.id in found_ids:
            raise Exception("Multiple Sounds on search.sound")
        found_ids.append(result.id)
        count += 1

    assert count >= 50

    count = 0
    found_ids = []
    for result in api.search.hashtags("funny", count=50):
        if result.id in found_ids:
            raise Exception("Multiple Users on search.user")
        found_ids.append(result.id)
        count += 1

    assert count >= 50


def test_video():
    count = 0
    found_ids = []
    for video in api.search.videos("therock", count=50):
        if video.id in found_ids:
            raise Exception("Duplicate Video on search.videos")
        found_ids.append(video.id)
        count += 1

    assert count >= 50


def test_users_alternate():
    count = 0
    found_ids = []
    for user in api.search.users_alternate("therock", count=50):
        if user.user_id in found_ids:
            raise Exception("Multiple Users on search.user")
        found_ids.append(user.user_id)
        count += 1

    assert count >= 50
