from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get("ms_token", None)  # set your own ms_token
sound_id = "7016547803243022337"


async def sound_videos():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        async for sound in api.sound(id=sound_id).videos(count=30):
            print(sound)
            print(sound.as_dict)


if __name__ == "__main__":
    asyncio.run(sound_videos())
