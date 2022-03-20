from TikTokApi import TikTokApi
import os


def test_trending_videos():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        count = 0
        for video in api.trending.videos(count=100):
            count += 1

        assert count >= 100
