from TikTokApi import TikTokApi
import os

api = TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None))


def test_trending_videos():
    count = 0
    for video in api.trending.videos(count=100):
        count += 1

    assert count >= 100
