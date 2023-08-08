from TikTokApi import TikTokApi
import os
import logging
import pytest

ms_token = os.environ.get("ms_token", None)


@pytest.mark.asyncio
async def test_hashtag_videos():
    api = TikTokApi(logging_level=logging.INFO)
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        tag = api.hashtag(name="funny")
        video_count = 0
        async for video in tag.videos(count=30):
            video_count += 1

        assert video_count >= 30


@pytest.mark.asyncio
async def test_hashtag_videos_multi_page():
    api = TikTokApi(logging_level=logging.INFO)
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        tag = api.hashtag(name="funny", id="5424")
        video_count = 0
        async for video in tag.videos(count=100):
            video_count += 1

        assert video_count >= 30


@pytest.mark.asyncio
async def test_hashtag_info():
    api = TikTokApi(logging_level=logging.INFO)
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        tag = api.hashtag(name="funny")
        await tag.info()

        assert tag.id == "5424"
        assert tag.name == "funny"


@pytest.mark.asyncio
async def test_non_latin1():
    api = TikTokApi(logging_level=logging.INFO)
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        tag = api.hashtag(name="селфи")
        await tag.info()

        assert tag.name == "селфи"
        assert tag.id == "4385126"
