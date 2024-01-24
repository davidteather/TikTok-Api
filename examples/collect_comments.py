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

async def get_comments(video_info, ms_token):
    async with TikTokApi() as api:
        # await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, headless=True, override_browser_args=["--incognito"])
        await api.close_sessions()
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        comments = []
        try:
            video = api.video(video_info['videoId'])
            commentCount = video_info['commentCount']
            print(f"コメント数：{commentCount}")
        except Exception as e:
            print(e)
            print("動画の取得に失敗しました")
            await api.close_sessions()
            return False
        try:
            async for comment in video.comments(count=commentCount):
                c = comment.as_dict
                comments.extend(clean_comment(c))
                if len(comments)%100 == 0:
                    print(f"{len(comments)}/{commentCount}")
        except Exception as e:
            print(e)
            print("コメントの取得に失敗しました")
            await api.close_sessions()
            return False

        await api.close_sessions()
        print(f"コメントの取得に成功しました：{len(comments)}")
        return comments

if __name__ == "__main__":
    tracemalloc.start()
    # ms_token = "nvUOkAnO1TLLSx8MJcpFGsx_su5bgsxe3oiEwwVVdtqDJUq0Dqfv37YjVSp1xPgekNFAOmrpFvlHLrVJ0XNUtQ33Tnk_cZYmDrh78ThklZBIP8lcTXk5P7B4ZgzsAKUc1KCcGB_sP8QVDNQT"  # set your own ms_token
    
    # フォルダ名を取得
    folder_path = "data/Hashtag"
    files = glob.glob(f"{folder_path}/*")
    files = [os.path.basename(f) for f in files]

    for file_name in files:
        comments = []
        error_ids = []

        print(f"ファイル：{file_name}")
        destination_folder = f'{folder_path}/{file_name}'
    
        #     file_name = input("Enter channel name:")
        #     if channel == "q":
        #         break
        #     destination_folder = f'data/{file_name}'

        files = glob.glob(f"{destination_folder}/*")
        break_flag = False
        for file in files:
            file = os.path.basename(file)
            if "comments" in file:
                print("コメントのJSONファイルが存在します")
                break_flag = True
                break
        if break_flag:
            continue
        
        try:
            file = glob.glob(f"{destination_folder}/{file_name}_videos.json")[0]
            with open(file, 'r', encoding='utf-8') as f:
                videos = json.load(f)
        except:
            print("動画情報のJSONファイルが存在しません")
            continue

        print(f"動画数：{len(videos)}")

        for i, video_info in enumerate(videos):
            if video_info['commentCount'] == 0:
                print(f"{i+1}/{len(videos)}番目の動画のコメントはありません：\n{video_info['title'][:min(100, len(video_info['title']))]}")
                continue

            print(f"{file_name}{i+1}/{len(videos)}番目の動画のコメントを取得します：{video_info['title'][:min(30, len(video_info['title']))]}")
            ms_token = os.environ.get("ms_token", None)
            tmp_c = asyncio.run(get_comments(video_info, ms_token))
            time.sleep(3)
            if tmp_c == False:
                error_ids.append(video_info)
                continue
            comments.extend(tmp_c)
            
            if (i+1)%100 == 0:
                comments_file_path = os.path.join(destination_folder, f'{file_name}_comments{i+1}.json')
                with open(comments_file_path, 'w', encoding='UTF-8') as json_file:
                    json.dump(comments, json_file, indent=2, ensure_ascii=False)
                error_ids.append(videos[i+1:])
                error_ids_file_path = os.path.join(destination_folder, f'{file_name}_error_ids.json')
                with open(error_ids_file_path, 'w', encoding='UTF-8') as json_file:
                    json.dump(error_ids, json_file, indent=2, ensure_ascii=False)

        comments_file_path = os.path.join(destination_folder, f'{file_name}_comments.json')
        with open(comments_file_path, 'w', encoding='UTF-8') as json_file:
            json.dump(comments, json_file, indent=2, ensure_ascii=False)
        if error_ids != []:
            error_ids_file_path = os.path.join(destination_folder, f'{file_name}_error_ids.json')
            with open(error_ids_file_path, 'w', encoding='UTF-8') as json_file:
                json.dump(error_ids, json_file, indent=2, ensure_ascii=False)

        print(f"コメント数：{len(comments)}")
        print(f"コメントを保存しました：{comments_file_path}")
        winsound.Beep(440, 1500)  # 440Hzの音を1.5秒間再生