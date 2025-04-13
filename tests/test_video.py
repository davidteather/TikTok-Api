from TikTokApi import TikTokApi
import os
import pytest

ms_token = os.environ.get("ms_token", None)
headless = os.environ.get("headless", "True").lower() == "true"


@pytest.mark.asyncio
async def test_video_id_from_url():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"), headless=headless)

        expected_id = "7074717081563942186"
        video = api.video(
            url="https://www.tiktok.com/@davidteathercodes/video/7074717081563942186"
        )

        assert video.id == expected_id

        # mobile_url = "https://www.tiktok.com/t/ZT8LCfcUC/"
        # video = api.video(url=mobile_url)

        # assert video.id == expected_id


@pytest.mark.asyncio
async def test_video_info():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"), headless=headless)
        video_id = "7074717081563942186"
        video = api.video(
            url="https://www.tiktok.com/@davidteathercodes/video/7074717081563942186"
        )

        data = await video.info()

        assert data["id"] == video_id
        video.author.username = "davidteathercodes"


@pytest.mark.asyncio
async def test_video_bytes():
    pytest.skip("Not implemented yet")
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"), headless=headless)
        video_id = "7107272719166901550"
        video = api.video(id=video_id)

        data = await video.bytes()
        assert len(data) > 10000


@pytest.mark.asyncio
async def test_related_videos():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"), headless=headless)
        video_id = "7107272719166901550"
        video = api.video(id=video_id)
        count = 0
        async for related_video in video.related_videos(count=10):
            print(related_video)
            count += 1

        assert count >= 10
