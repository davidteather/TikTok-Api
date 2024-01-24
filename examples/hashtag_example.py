from TikTokApi import TikTokApi
import asyncio
import os
import json
import datetime

def clean_video(v):
    author_info = v.get("author", {})
    stats = v.get("stats", {})
    video = {
        'etag': v.get("id", ""),
        'videoId': v.get("id", ""),
        'publishedDate': v.get("createTime", ""),
        'channelId': author_info.get("uniqueId", ""),
        'channelTitle': author_info.get("nickname", ""),
        'title': v.get("desc", ""),
        'description': "",  
        'thumbnails': author_info.get("avatarLarger", ""),
        'categoryId': "",  
        'duration': v.get("video", {}).get("duration", 0),
        'caption': "",
        'licensedContent': False,
        'contentRating': "", 
        'viewCount': stats.get("playCount", 0),
        'favoriteCount': stats.get("collectCount", 0),
        'commentCount': stats.get("commentCount", 0),
        'likeCount': stats.get("diggCount", 0),
        'shareCount': stats.get("shareCount", 0),
        'defaultLanguage': "",
        'tags': [tag.get("hashtagName", "") for tag in v.get("textExtra", [])],
        'challenges': [challenge.get("title", "") for challenge in v.get("challenges", [])]
    }
    return video

async def get_hashtag_videos(hashtag, n):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        tag = api.hashtag(name=hashtag)
        video_count = n
        videos = []
        async for video in tag.videos(count=video_count):
            v = video.as_dict
            # v = clean_video(v)
            videos.append(v)
    return videos

if __name__ == "__main__":
    ms_token = "nvUOkAnO1TLLSx8MJcpFGsx_su5bgsxe3oiEwwVVdtqDJUq0Dqfv37YjVSp1xPgekNFAOmrpFvlHLrVJ0XNUtQ33Tnk_cZYmDrh78ThklZBIP8lcTXk5P7B4ZgzsAKUc1KCcGB_sP8QVDNQT"  # set your own ms_token
    n = 10000
    hashtags = ["地震","能登半島地震"]
    while hashtags:
        # hashtag = input("Enter hashtag name:")
        # if hashtag == "q":
        #     break
        hashtag = hashtags.pop(0)
        print(f"ハッシュタグ：{hashtag}")
        try:
            videos = asyncio.run(get_hashtag_videos(hashtag, n))
            
            # Save user_info as JSON
            destination_folder = f'c:/Users/Koki/Documents/東大/TikTok-Api/data/Hashtag/H_{hashtag}'
            os.makedirs(destination_folder, exist_ok=True)  # 移動先フォルダが存在しない場合は作成する
            # user_file_path = os.path.join(destination_folder, f'{channel}_channel.json')  # ファイル名は適宜変更してください
            # with open(user_file_path, 'w') as json_file:
            #     json.dump(user_info, json_file, indent=2)

            # Save video_info as JSON
            today = datetime.date.today()
            videos_file_path = os.path.join(destination_folder, f'H_{hashtag}_videos_{today}_raw.json')  # ファイル名は適宜変更してください
            with open(videos_file_path, 'w', encoding='UTF-8') as json_file:
                json.dump(videos, json_file, indent=2, ensure_ascii=False)
            print("Done")
        except Exception as e:
            print("エラー：", e)
