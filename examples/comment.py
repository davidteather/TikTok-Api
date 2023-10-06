from TikTokApi import TikTokApi
import asyncio
import os
import json
import glob
import re
import winsound

async def get_comments(videoId, ms_token):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=1)
        comments = []
        video = api.video(videoId['videoId'])
        commentCount = int(videoId['commentCount'])
        print(commentCount)
        async for comment in video.comments(count=commentCount):
            c = comment.as_dict
            comments.append(c)
            if len(comments)%100 == 0:
                print(f"{len(comments)}/{commentCount}")
        
        comments_file_path = os.path.join(destination_folder, f'{channel}_{videoId["title"]}_comments.json')  # ファイル名は適宜変更してください
        with open(comments_file_path, 'w') as json_file:
            json.dump(comments, json_file, indent=2)

if __name__ == "__main__":
    ms_token = os.environ.get("ms_token", None)  # set your own ms_token
    # channel = input("Enter channel name:")
    channel = "atsuhiko_nakata"

    file = glob.glob(f"data/{channel}/{channel}_videos.json")[0]
    with open(file, 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    # Save comments as JSON
    destination_folder = f'data/{channel}'
    os.makedirs(destination_folder, exist_ok=True)  # 移動先フォルダが存在しない場合は作成する

    asyncio.run(get_comments(videos[4], ms_token))
    
    winsound.Beep(440, 1500)  # 440Hzの音を1.5秒間再生