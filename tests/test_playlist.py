from TikTokApi import TikTokApi
import os
import pytest

playlist_id="7281443725770476321"
playlist_name="Doctor Who"
playlist_creator="bbc"

ms_token = os.environ.get("ms_token", None)
headless = os.environ.get("headless", "True").lower() == "true"


@pytest.mark.asyncio
async def test_playlist_info():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, headless=headless)
        playlist = api.playlist(id=playlist_id)
        await playlist.info()

        assert playlist.id == playlist_id
        assert playlist.name == playlist_name
        assert playlist.creator.username == playlist_creator
        assert playlist.video_count > 0
        assert playlist.cover_url is not None
        assert playlist.as_dict is not None

@pytest.mark.asyncio
async def test_playlist_videos():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, headless=headless)
        playlist = api.playlist(id=playlist_id)

        count = 0
        async for video in playlist.videos(count=30):
            count += 1

        assert count >= 30
