from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get("ms_token", None)  # set your own ms_token


async def search_videos():
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=3,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
        )

        keyword = "funny cats"
        cursor = 0
        max_videos = 30

        search_url = "https://www.tiktok.com/api/search/item/full/"

        while True:
            params = {
                "keyword": keyword,
                "count": 10,
                "cursor": cursor,
                "source": "search_video",
            }

            response = await api.make_request(url=search_url, params=params)

            if "item_list" in response:
                for video in response["item_list"]:
                    print(f"Description: {video.get('desc', 'N/A')}")
                    print(f"Author: @{video.get('author', {}).get('uniqueId', 'N/A')}")
                    print(f"Video ID: {video.get('id', 'N/A')}")
                    print()

            cursor = response.get("cursor", 0)
            has_more = response.get("has_more", False)

            if not has_more or len(response.get("item_list", [])) >= max_videos:
                break


if __name__ == "__main__":
    asyncio.run(search_videos())
