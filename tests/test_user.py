from TikTokApi import TikTokApi
import os
import pytest

username = "charlidamelio"
user_id = "5831967"
sec_uid = "MS4wLjABAAAA-VASjiXTh7wDDyXvjk10VFhMWUAoxr8bgfO1kAL1-9s"

ms_token = os.environ.get("ms_token", None)


@pytest.mark.asyncio
async def test_user_info():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        user = api.user(username=username)
        await user.info()

        assert user.username == username
        assert user.user_id == user_id
        assert user.sec_uid == sec_uid


@pytest.mark.asyncio
async def test_user_videos():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        user = api.user(username=username, sec_uid=sec_uid, user_id=user_id)

        count = 0
        async for video in user.videos(count=30):
            count += 1

        assert count >= 30


@pytest.mark.asyncio
async def test_user_likes():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        user = api.user(
            username="publicliketest",
            sec_uid="MS4wLjABAAAAHjhwCIwmvzVZfRrDAZ2aZy74LciLnoyaPfM2rrX9N7bwbWMFuwTFG4YrByYvsH5c",
        )

        count = 0
        async for video in user.liked(count=30):
            count += 1

        assert count >= 30
