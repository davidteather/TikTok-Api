from TikTokApi import TikTokApi
import asyncio
import os
import json

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

def clean_user(user):
    u = user.get("userInfo", {}).get("user", {})
    s = user.get("userInfo", {}).get("stats", {})
    user = {
        'etag': u.get("id", ""),
        'channelId': u.get("uniqueId", ""),
        'channelTitle': u.get("nickname", ""),
        'description': u.get("signature", ""),
        'thumbnails': u.get("avatarLarger", ""),
        'link': u.get("bioLink", {}).get("link", ""),
        'commerceUser': u.get("commerceUserInfo", {}).get("commerceUser", False),
        'likeCount': s.get("diggCount", 0),
        'followerCount': s.get("followerCount", 0),
        'followingCount': s.get("followingCount", 0),
        'heartCount': s.get("heartCount", 0),
        'videoCount': s.get("videoCount", 0),
    }
    return user

async def get_videos(channel):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        print("Sessions created")
        user = api.user(username=channel)
        u = await user.info()
        user_info = clean_user(u)
        print("User info collected")

        video_count = user_info["videoCount"]
        videos = []
        async for video in user.videos(count=video_count):
            v = video.as_dict
            videos.append(clean_video(v))
    
    return user_info, videos

if __name__ == "__main__":
    ms_token = "nvUOkAnO1TLLSx8MJcpFGsx_su5bgsxe3oiEwwVVdtqDJUq0Dqfv37YjVSp1xPgekNFAOmrpFvlHLrVJ0XNUtQ33Tnk_cZYmDrh78ThklZBIP8lcTXk5P7B4ZgzsAKUc1KCcGB_sP8QVDNQT"  # set your own ms_token
    while True:
        channel = input("Enter channel name:")
        if channel == "q":
            break
        # channel = "hiroshima_pref"
        try:
            user_info, videos = asyncio.run(get_videos(channel))
            
            # Save user_info as JSON
            destination_folder = f'c:/Users/Koki/Documents/東大/TikTok-Api/data/{channel}'
            os.makedirs(destination_folder, exist_ok=True)  # 移動先フォルダが存在しない場合は作成する
            user_file_path = os.path.join(destination_folder, f'{channel}_channel.json')  # ファイル名は適宜変更してください
            with open(user_file_path, 'w') as json_file:
                json.dump(user_info, json_file, indent=2)

            # Save video_info as JSON
            videos_file_path = os.path.join(destination_folder, f'{channel}_videos.json')  # ファイル名は適宜変更してください
            with open(videos_file_path, 'w') as json_file:
                json.dump(videos, json_file, indent=2)
            print("Done")
        except:
            print("Error")