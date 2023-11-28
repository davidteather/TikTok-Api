from TikTokApi import TikTokApi
import os
import pytest

ms_token = os.environ.get("ms_token", None)

@pytest.mark.asyncio
async def test_users_single_page():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        count = 0
        async for user in api.search.users("therock", count=10):
            count += 1

        assert count >= 10

#@pytest.mark.asyncio
@pytest.mark.skip(reason="Known issue, see #1088 (https://github.com/davidteather/TikTok-Api/issues/1088)")
async def test_users_multi_page():
    api = TikTokApi()
    async with api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        count = 0
        async for user in api.search.users("therock", count=50):
            count += 1

        assert count >= 50
