from tiktok import TikTokApi
import asyncio
import os
import json
import glob
import re
import winsound
import time

def unescape_unicode(text):
    return re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), text)

def clean_comment(c):
    comments = []
    comment = {
        'etag': c.get('cid'),
        'videoId': c.get('aweme_id'),
        'text': unescape_unicode(c.get("text")),
        'commentLanguage': c.get('comment_language'),
        'author': unescape_unicode(c.get("user", {}).get("nickname")),
        'authorId': c.get('user', {}).get('unique_id'),
        'likeCount': c.get('digg_count'),
        'replyCount': c.get('reply_comment_total'),
        'commentDate': c.get('create_time'),
        'replyToId': c.get('reply_id'),
    }
    # print(unescape_unicode(c.get("text")))
    if c['reply_comment'] != None:
        reply_count = c.get('reply_comment_total')
        comment['replyCount'] = reply_count
        reply_comment = clean_comment(c['reply_comment'][0])
        comment['replyFromId'] = c['reply_comment'][0].get('cid')
        comments.append(comment)
        comments.extend(reply_comment)
    
    else:
        comment['replyCount'] = 0
        comment['replyFromId'] = 0
        comments.append(comment)
        
    return comments

async def get_comments(video_info, ms_token, i):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=1)
        
        comments = []
        print(f"{i+1}番目の動画：{video_info['title']}のコメントを取得します")
        video = api.video(video_info['videoId'])
        commentCount = video_info['commentCount']
        print(f"コメント数：{commentCount}")
        async for comment in video.comments(count=commentCount):
            c = comment.as_dict
            comments.extend(clean_comment(c))
            if len(comments)%100 == 0:
                print(f"{len(comments)}/{commentCount}")
        
        comments_file_path = os.path.join(destination_folder, f'{channel}_comments{i+1}.json')  # ファイル名は適宜変更してください
        with open(comments_file_path, 'w') as json_file:
            json.dump(comments, json_file, indent=2)

        # comments = []
        # for i, video_info in enumerate(videos):
        #     print(f"{i+1}/{len(videos)}番目の動画：{video_info['title']}のコメントを取得します")
        #     video = api.video(video_info['videoId'])
        #     commentCount = video_info['commentCount']
        #     print(commentCount)
        #     comments_list = video.comments(count=commentCount)
        #     async for comment in comments_list:
        #         c = comment.as_dict
        #         comments.extend(clean_comment(c))
        #         if len(comments)%100 == 0:
        #             print(f"{len(comments)}/{commentCount}")
            
        # comments_file_path = os.path.join(destination_folder, f'{channel}_comments.json')  # ファイル名は適宜変更してください
        # with open(comments_file_path, 'w') as json_file:
        #     json.dump(comments, json_file, indent=2)
            


if __name__ == "__main__":
    ms_token = os.environ.get("ms_token", None)  # set your own ms_token
    # channel = input("Enter channel name:")
    channel = "katoyuridayo"

    file = glob.glob(f"data/{channel}/{channel}_videos.json")[0]
    with open(file, 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    # Save comments as JSON
    destination_folder = f'data/{channel}'
    os.makedirs(destination_folder, exist_ok=True)  # 移動先フォルダが存在しない場合は作成する

    for i, video_info in enumerate(videos):
        asyncio.run(get_comments(video_info, ms_token, i)) 
        time.sleep(1)

    
    winsound.Beep(440, 1500)  # 440Hzの音を1.5秒間再生
