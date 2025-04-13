from TikTokApi import TikTokApi
import os
import pytest

video_id = 7248300636498890011
ms_token = os.environ.get("ms_token", None)
headless = os.environ.get("headless", "True").lower() == "true"


@pytest.mark.asyncio
async def test_comment_page():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"), headless=headless)
        video = api.video(id=video_id)
        count = 0
        async for comment in video.comments(count=100):
            count += 1

        assert count >= 100
