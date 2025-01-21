from TikTokApi import TikTokApi
import asyncio
import os

video_id = 7248300636498890011
ms_token = os.environ.get("ms_token", None)  # set your own ms_token


async def get_comments():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        video = api.video(id=video_id)
        count = 0
        async for comment in video.comments(count=30):
            print(comment)
            print(comment.as_dict)


if __name__ == "__main__":
    asyncio.run(get_comments())
