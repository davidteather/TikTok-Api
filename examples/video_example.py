from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get(
    "ms_token", None
)  # set your own ms_token, think it might need to have visited a profile


async def get_video_example():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        video = api.video(
            url="https://www.tiktok.com/@davidteathercodes/video/7074717081563942186"
        )

        async for related_video in video.related_videos(count=10):
            print(related_video)
            print(related_video.as_dict)

        video_info = await video.info()  # is HTML request, so avoid using this too much
        print(video_info)


if __name__ == "__main__":
    asyncio.run(get_video_example())
