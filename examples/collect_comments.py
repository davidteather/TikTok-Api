from TikTokApi import TikTokApi
import asyncio
import os
import json
import glob
import re
import winsound
import time
import tracemalloc

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
        comment['replyFromId'] = "0"
        comments.append(comment)
        
    return comments

async def get_comments(video_info, ms_token, i):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=1)
        
        comments = []
        try:
            video = api.video(video_info['videoId'])
            commentCount = video_info['commentCount']
            print(f"コメント数：{commentCount}")
            async for comment in video.comments(count=commentCount):
                c = comment.as_dict
                comments.extend(clean_comment(c))
                if len(comments)%100 == 0:
                    print(f"{len(comments)}/{commentCount}")
        except Exception as e:
            print(e)
            print("コメントの取得に失敗しました")

        await api.close_sessions()
        return comments

if __name__ == "__main__":
    tracemalloc.start()
    ms_token = "nvUOkAnO1TLLSx8MJcpFGsx_su5bgsxe3oiEwwVVdtqDJUq0Dqfv37YjVSp1xPgekNFAOmrpFvlHLrVJ0XNUtQ33Tnk_cZYmDrh78ThklZBIP8lcTXk5P7B4ZgzsAKUc1KCcGB_sP8QVDNQT"  # set your own ms_token
    # channel = "taro_koho"
    while True:
        comments = []
        channel = input("Enter channel name:")
        if channel == "q":
            break
        destination_folder = f'data/{channel}'

        try:
            file = glob.glob(f"{destination_folder}/{channel}_videos.json")[0]
            with open(file, 'r', encoding='utf-8') as f:
                videos = json.load(f)
        except:
            print("動画情報のJSONファイルが存在しません")
            continue

        print(f"動画数：{len(videos)}")

        for i, video_info in enumerate(videos):
            if video_info['commentCount'] == 0:
                print(f"{i+1}/{len(videos)}番目の動画のコメントはありません：{video_info['title']}")
                continue
            print(f"{i+1}/{len(videos)}番目の動画のコメントを取得します：{video_info['title']}")
            tmp_c = asyncio.run(get_comments(video_info, ms_token, i)) 
            comments.extend(tmp_c)

        comments_file_path = os.path.join(destination_folder, f'{channel}_comments.json')  # ファイル名は適宜変更してください
        with open(comments_file_path, 'w') as json_file:
            json.dump(comments, json_file, indent=2)

        print(f"コメント数：{len(comments)}")
        print(f"コメントを保存しました：{comments_file_path}")
        winsound.Beep(440, 1500)  # 440Hzの音を1.5秒間再生