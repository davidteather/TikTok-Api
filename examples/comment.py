from TikTokApi import TikTokApi
import asyncio
import os
import json
import glob
import re
import winsound
import pandas as pd

async def get_comments(videoId, comment_count, ms_token, i, destination_folder, channel):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=1)
        comments = []
        video = api.video(videoId)#['videoId'])
        commentCount = comment_count
        print("総コメント数：", commentCount)
        try:
            async for comment in video.comments(count=commentCount):
                c = comment.as_dict
                comments.append(c)
                if len(comments)%100 == 0:
                    print(f"コメント：{len(comments)}/{commentCount}")
        except Exception as e:
            print(e)
            print("コメントの取得に失敗しました")
            await api.close_sessions()
            return comments
        
        # comments = pd.DataFrame(comments)
        # comments.to_json(f"{destination_folder}/{channel}_comments{i}.json", orient="records", force_ascii=False)
        print(f"コメントの取得に成功しました：{len(comments)}")
        await api.close_sessions()
        return comments

if __name__ == "__main__":
    ms_token = os.environ.get("ms_token", None)  # set your own ms_token
    # channel = input("Enter channel name:")
    list = [["津波",400],["地震",0]]
    for channel, start in list:
        channel = "H_" + channel
        print(f"チャンネル：{channel}")

        folder_path = "data/Hashtag"
        # fileが存在するか確認
        file = glob.glob(f"{folder_path}/{channel}/{channel}_error_ids.json")
        if len(file) == 0:
            file = glob.glob(f"{folder_path}/{channel}/{channel}_videos_raw.json")
            k = ""
        else:
            k = "error"
        with open(file[0], 'r', encoding='utf-8') as f:
            videos = json.load(f)

        # Save comments as JSON
        destination_folder = f'{folder_path}/{channel}'
        if start == 0:
            comment_list = []
            error_ids = []
        else:
            comment_list = pd.read_json(f"{destination_folder}/{channel}_comments{start}.json", orient='records')
            comment_list = comment_list.to_dict(orient='records')
            error_ids = pd.read_json(f"{destination_folder}/{channel}_error_ids{start}.json", orient='records')
            error_ids = error_ids.to_dict(orient='records')
            print(f"コメントの総数：{len(comment_list)}")
            print(f"エラーの総数：{len(error_ids)}")
        # Get comments
        for i in range(start, len(videos)):
            if k != "error":
                comment_count = videos[i]["stats"]['commentCount']
                videoId = videos[i]['id']
                if comment_count == 0:
                    print(f"{i+1}/{len(videos)}番目の動画のコメントはありません：\n{videos[i]['desc'][:min(100, len(videos[i]['desc']))]}")
                else:
                    print(f"{channel}{i+1}/{len(videos)}番目の動画のコメントを取得します：{videos[i]['desc'][:min(30, len(videos[i]['desc']))]}")
                    c = asyncio.run(get_comments(videoId, comment_count, ms_token, i, destination_folder, channel))
                    if len(c) > 0:
                        comment_list.extend(c)
                    else:
                        print("コメントの取得に失敗しました")
                        error_ids.append(videos[i])
            if (i+1)%50 == 0:
                comment_list_tmp = pd.DataFrame(comment_list)
                comment_list_tmp.to_json(f"{destination_folder}/{channel}_comments{i+1}{k}.json", orient="records", force_ascii=False, default_handler=str, indent=2)
                error_ids_tmp = pd.DataFrame(error_ids)
                error_ids_tmp.to_json(f"{destination_folder}/{channel}_error_ids{i+1}{k}.json", orient="records", force_ascii=False, default_handler=str, indent=2)
                # 100件前に保存したファイルを消す
                try:
                    os.remove(f"{destination_folder}/{channel}_comments{i-49}{k}.json")
                    os.remove(f"{destination_folder}/{channel}_error_ids{i-49}{k}.json")
                except Exception as e:
                    print(e)
                    # destination_folderの中のファイルを全て表示
                    files = glob.glob(f"{destination_folder}/*")
                    print(files)
                    print("ファイルの削除に失敗しました")
                    continue

        # Save comments as JSON
        comment_list = pd.DataFrame(comment_list)
        comment_list.to_json(f"{destination_folder}/{channel}_comments{k}.json", orient='records', date_format='iso', force_ascii=False, default_handler=str, indent=2)
        error_ids = pd.DataFrame(error_ids)
        error_ids.to_json(f"{destination_folder}/{channel}_error_ids.json", orient='records', date_format='iso', force_ascii=False, default_handler=str, indent=2)
        try:
            os.remove(f"{destination_folder}/{channel}_comments{i-(i%50)}{k}.json")
            os.remove(f"{destination_folder}/{channel}_error_ids{i-(i%50)}{k}.json")
        except Exception as e:
            print(e)
            # destination_folderの中のファイルを全て表示
            files = glob.glob(f"{destination_folder}/*")
            print(files)
            print("ファイルの削除に失敗しました")
            continue
        winsound.Beep(440, 1500)  # 440Hzの音を1.5秒間再生