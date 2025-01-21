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

        async for playlist in user.playlists(count=3):
            print(playlist)
            print(playlist.name)

            async for video in playlist.videos(count=3):
                print(video)
                print(video.url)

if __name__ == "__main__":
    asyncio.run(user_example())
