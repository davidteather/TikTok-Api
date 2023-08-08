from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get(
    "ms_token", None
)  # set your own ms_token, needs to have done a search before for this to work


async def search_users():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        async for user in api.search.users("david teather", count=10):
            print(user)


if __name__ == "__main__":
    asyncio.run(search_users())
