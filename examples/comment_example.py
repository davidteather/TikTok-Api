from TikTokApi import TikTokApi
import asyncio
import os

video_id = 7259386491149831426
ms_token = "nvUOkAnO1TLLSx8MJcpFGsx_su5bgsxe3oiEwwVVdtqDJUq0Dqfv37YjVSp1xPgekNFAOmrpFvlHLrVJ0XNUtQ33Tnk_cZYmDrh78ThklZBIP8lcTXk5P7B4ZgzsAKUc1KCcGB_sP8QVDNQT"  # set your own ms_token
    

async def get_comments():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        video = api.video(id=video_id)
        print(f"video:{video}")
        async for comment in video.comments(count=100):
            print(f"comment:{comment.text}")
            # print(comment.as_dict)


if __name__ == "__main__":
    asyncio.run(get_comments())