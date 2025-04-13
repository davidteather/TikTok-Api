from TikTokApi import TikTokApi
import os
import pytest

ms_token = os.environ.get("ms_token", None)
headless = os.environ.get("headless", "True").lower() == "true"
song_id = "7016547803243022337"


@pytest.mark.asyncio
async def test_sound_videos():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"), headless=headless)
        sound = api.sound(id=song_id)
        video_count = 0
        async for video in sound.videos(count=100):
            video_count += 1

        assert video_count >= 100


@pytest.mark.asyncio
async def test_sound_info():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"), headless=headless)
        sound = api.sound(id=song_id)
        await sound.info()
        assert sound.id == song_id
        assert sound.title == "Face Off - Dwayne Johnson"
        assert sound.duration == 60
