from TikTokApi import TikTokApi
import os

api = TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None))


def test_trending_videos():
    count = 0
    for video in api.trending.videos(count=100):
        count += 1

    assert count >= 100


def test_discover_type():
    count = 0
    found_ids = []
    for result in api.trending.users():
        if result.user_id in found_ids:
            raise Exception("Multiple Users on trending.user")
        found_ids.append(result.user_id)
        count += 1

    assert count >= 50

    count = 0
    found_ids
    for result in api.trending.sounds():
        if result.id in found_ids:
            raise Exception("Multiple Sounds on trending.sound")
        found_ids.append(result.id)
        count += 1

    assert count >= 50

    count = 0
    found_ids = []
    for result in api.trending.hashtags():
        if result.id in found_ids:
            raise Exception("Multiple Users on trending.user")
        found_ids.append(result.id)
        count += 1

    assert count >= 50
