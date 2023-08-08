from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get(
    "ms_token", None
)  # set your own ms_token, think it might need to have visited a profile


async def user_example():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        user = api.user("therock")
        user_data = await user.info()
        print(user_data)

        async for video in user.videos(count=30):
            print(video)
            print(video.as_dict)


if __name__ == "__main__":
    asyncio.run(user_example())
