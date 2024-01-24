from TikTokApi import TikTokApi
import asyncio
import os
import json

video_id = 7235267734261484801
ms_token = os.environ.get("ms_token", None)  # set your own ms_token

async def get_video_example():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        video = api.video(
            url=f"https://www.tiktok.com/@jinguji_ai_/video/{video_id}"
        )

        related_videos_data = []
        async for related_video in video.related_videos(count=10):
            related_videos_data.append(related_video.as_dict)
            #print(related_video)
            #print(related_video.as_dict)

        video_info = await video.info()  # is HTML request, so avoid using this too much
        print(video_info)

        return video_info, related_videos_data


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    video_info, related_videos = loop.run_until_complete(get_video_example())

    # # Save video_info as JSON
    # with open("video_info.json", "w") as json_file:
    #     json.dump(video_info, json_file, indent=4)

    # # Save related_videos as JSON
    # with open("related_videos.json", "w") as json_file:
    #     json.dump(related_videos, json_file, indent=4)
