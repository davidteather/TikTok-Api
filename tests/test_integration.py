from TikTokApi import TikTokApi
import os
import pytest

ms_token = os.environ.get("ms_token", None)
headless = os.environ.get("headless", "True").lower() == "true"


@pytest.mark.asyncio
async def test_hashtag_videos():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"), headless=headless)
        tag_name = "funny"
        count = 0
        async for video in api.hashtag(name=tag_name).videos(count=1):
            count += 1
            tag_included = False
            for tag in video.hashtags:
                if tag.name == tag_name:
                    tag_included = True

            assert tag_included

            # Test sound on video.
            assert video.sound is not None
            assert video.sound.id is not None

            # Test author.
            assert video.author is not None
            assert video.author.user_id is not None
            assert video.author.sec_uid is not None

        assert count > 0
