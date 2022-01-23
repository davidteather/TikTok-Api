from TikTokApi import TikTokApi
import os

api = TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None))


def test_discover_type():
    count = 0
    for result in api.search.users("therock", count=50):
        count += 1

    assert count >= 50

    count = 0
    for result in api.search.sounds("funny", count=50):
        count += 1

    assert count >= 50

    count = 0
    for result in api.search.hashtags("funny", count=50):
        count += 1

    assert count >= 50


def test_users_alternate():
    count = 0
    for user in api.search.users_alternate("therock", count=50):
        count += 1

    assert count >= 50
