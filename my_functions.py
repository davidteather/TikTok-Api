import os
import re
import json
import time
import copy
import string
import shutil
import random
import winsound
import requests
import numpy as np
import pandas as pd
import seaborn as sns
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from bs4 import BeautifulSoup
from collections import Counter
from langdetect import detect_langs
from langdetect.lang_detect_exception import LangDetectException
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from networkx.algorithms.community import greedy_modularity_communities, label_propagation_communities
from sklearn.cluster import SpectralClustering

# 日本語フォントのパスを指定（使用するフォントに応じてパスを変更してください）
font_path = "C:\Windows\Fonts\msyh.ttc"
# フォントマネージャにフォントを登録
font_prop = fm.FontProperties(fname=font_path)

# JSONファイルを読み込みDataFrameに変換
def read_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # DataFrameに変換する
    df = pd.DataFrame(data)
    return df

# ファイルの結合
def merge_json(file_paths):
    merged_data = []
    seen_ids = set()  # これまでに見たidのセット
    
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
            for item in data:
                if item['etag'] not in seen_ids:  # idがまだ見られていない場合のみ追加
                    merged_data.append(item)
                    seen_ids.add(item['etag'])
            
            print(file_path, len(data))
    
    return merged_data

def get_data_or_none(dictionary, keys, default=np.nan):
    """
    ネストされた辞書からデータを取得する。データが存在しない場合、デフォルト値を返す。
    keys: 辞書のキーのリストまたはタプル
    """
    try:
        for key in keys:
            dictionary = dictionary[key]
        return dictionary
    except (KeyError, TypeError):
        return default
    
# ビデオからチャンネルIDを取得
def get_channel_id(video_id, youtube):
    # 動画の詳細情報を取得
    video_response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    # 動画の詳細情報からチャンネルIDを取得
    channel_id = video_response['items'][0]['snippet']['channelId']

    return channel_id

# チャンネルのすべての動画のIDを取得
def get_videos_from_channel(channel_id, youtube, save=True):
    # チャンネル情報を取得
    channel_response = youtube.channels().list(
        part='snippet',
        id=channel_id
    ).execute()
    channel = channel_response['items'][0]['snippet']['customUrl']

    # チャンネルの動画を取得
    videos = []
    next_page_token = None
    # 取得した動画のIDを格納するリスト
    video_ids = []

    while True:
        # チャンネルのプレイリストを取得
        channel_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        # プレイリストのIDを取得
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # プレイリストの動画を取得
        playlist_items_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=100,
            pageToken=next_page_token
        ).execute()

        for item in playlist_items_response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_ids.append(video_id)
            # 動画の詳細情報を取得
            v = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()['items'][0]
            
            video_data = {
                'etag': get_data_or_none(v, ('etag',)),
                'videoId': get_data_or_none(v, ('id',)),
                'publishedDate': get_data_or_none(v, ('snippet', 'publishedAt')),
                'channelId': get_data_or_none(v, ('snippet', 'channelId')),
                'channelTitle': get_data_or_none(v, ('snippet', 'channelTitle')),
                'title': get_data_or_none(v, ('snippet', 'title')),
                'description': get_data_or_none(v, ('snippet', 'description')),
                'thumbnails': get_data_or_none(v, ('snippet', 'thumbnails', 'default', 'url')),
                'categoryId': get_data_or_none(v, ('snippet', 'categoryId')),
                'duration': get_data_or_none(v, ('contentDetails', 'duration')),
                'caption': get_data_or_none(v, ('contentDetails', 'caption')),
                'licensedContent': get_data_or_none(v, ('contentDetails', 'licensedContent')),
                'contentRating': get_data_or_none(v, ('contentDetails', 'contentRating')),
                'viewCount': get_data_or_none(v, ('statistics', 'viewCount')),
                'favoriteCount': get_data_or_none(v, ('statistics', 'favoriteCount')),
                'commentCount': get_data_or_none(v, ('statistics', 'commentCount')),
                'likeCount': get_data_or_none(v, ('statistics', 'likeCount')),
                'defaultLanguage': get_data_or_none(v, ('snippet', 'defaultLanguage')),
                'tags': get_data_or_none(v, ('snippet', 'tags'))
            }
            
            videos.append(video_data)
        
        next_page_token = playlist_items_response.get('nextPageToken')

        if not next_page_token:
            break
        
    if save:
        # 結果をJSONファイルで保存
        destination_folder = f'data/{channel}'
        os.makedirs(destination_folder, exist_ok=True)  # 移動先フォルダが存在しない場合は作成する

        df_videos = pd.DataFrame(videos)
        df_videos.to_json(f'{destination_folder}/{channel}_videos.json', orient='records', date_format='iso')
        
    print(f"ビデオの数：{len(video_ids)}")
   
    return video_ids, channel

# 検索クエリから動画を取得
def get_videos_from_search(search_query, youtube, num_loop=20, channel_id=None, save=True):
    # 該当する動画を取得
    videos = []
    next_page_token = None
    # 取得した動画のIDを格納するリスト
    video_ids = []

    for _ in range(num_loop):
        # 検索結果の上位50件ずつを取得
        if channel_id:
            response = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                q=search_query,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
        else:
            response = youtube.search().list(
                part='snippet',
                q=search_query,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            
        for item in response['items']:
            try:
                video_id = item['id']['videoId']
                video_ids.append(video_id)
                # 動画の詳細情報を取得
                v = youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=video_id
                ).execute()['items'][0]

                video_data = {
                    'etag': get_data_or_none(v, ('etag',)),
                    'videoId': get_data_or_none(v, ('id',)),
                    'publishedDate': get_data_or_none(v, ('snippet', 'publishedAt')),
                    'channelId': get_data_or_none(v, ('snippet', 'channelId')),
                    'channelTitle': get_data_or_none(v, ('snippet', 'channelTitle')),
                    'title': get_data_or_none(v, ('snippet', 'title')),
                    'description': get_data_or_none(v, ('snippet', 'description')),
                    'thumbnails': get_data_or_none(v, ('snippet', 'thumbnails', 'default', 'url')),
                    'categoryId': get_data_or_none(v, ('snippet', 'categoryId')),
                    'duration': get_data_or_none(v, ('contentDetails', 'duration')),
                    'caption': get_data_or_none(v, ('contentDetails', 'caption')),
                    'licensedContent': get_data_or_none(v, ('contentDetails', 'licensedContent')),
                    'contentRating': get_data_or_none(v, ('contentDetails', 'contentRating')),
                    'viewCount': get_data_or_none(v, ('statistics', 'viewCount')),
                    'favoriteCount': get_data_or_none(v, ('statistics', 'favoriteCount')),
                    'commentCount': get_data_or_none(v, ('statistics', 'commentCount')),
                    'likeCount': get_data_or_none(v, ('statistics', 'likeCount')),
                    'defaultLanguage': get_data_or_none(v, ('snippet', 'defaultLanguage')),
                    'tags': get_data_or_none(v, ('snippet', 'tags'))
                }

                videos.append(video_data)
            except KeyError as e:
                print(f"An error occurred: {e}\nvideo_id：{item}　")
                pass
        
        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break
        
    if save:
        if channel_id:
            # チャンネル情報を取得
            channel_response = youtube.channels().list(
                part='snippet',
                id=channel_id
            ).execute()
            dir_name = channel_response['items'][0]['snippet']['customUrl']
        else:
            dir_name = search_query
        # 結果をJSONファイルで保存
        destination_folder = f'data/{dir_name}'
        os.makedirs(destination_folder, exist_ok=True)  # 移動先フォルダが存在しない場合は作成する

        df_videos = pd.DataFrame(videos)
        if channel_id:
            df_videos.to_json(f'{destination_folder}/{dir_name}_{search_query}_videos.json', orient='records', date_format='iso')
        else:
            df_videos.to_json(f'{destination_folder}/{search_query}_videos.json', orient='records', date_format='iso')
    print(f"ビデオの数：{len(video_ids)}")
   
    return video_ids
    
    
# チャンネルのすべての動画からすべてのコメントを取得
def get_comments(video_ids, youtube, channel, k="", save=True):
    print("コメント収集の開始")
    # 取得したコメントを格納するリスト
    comments = []
    
    # エラーとなった動画idを格納するリスト
    error_ids = []
    
    # 計測情報
    n = len(video_ids)
    n_tmp = 0
    start0_time = time.time()
    start_time = time.time()
    
    exit_outer_loop = False

    for i, video_id in enumerate(video_ids):
        next_page_token = None
        tmp_comments = []

        while True:
            try:
                # 動画のコメントスレッドを取得
                comment_response = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=100,
                    pageToken=next_page_token
                ).execute()
                # 動画のコメントスレッドを取得
                for c in comment_response["items"]:
                    comment_data = {
                        'etag': get_data_or_none(c, ('etag',)),
                        'videoId': get_data_or_none(c, ('snippet', 'videoId')),
                        'text': get_data_or_none(c, ('snippet', 'topLevelComment', 'snippet', 'textOriginal')),
                        'author': get_data_or_none(c, ('snippet', 'topLevelComment', 'snippet', 'authorDisplayName')),
                        'authorId': get_data_or_none(c, ('snippet', 'topLevelComment', 'snippet', 'authorChannelId', 'value')),
                        'likeCount': get_data_or_none(c, ('snippet', 'topLevelComment', 'snippet', 'likeCount')),
                        'replyCount': get_data_or_none(c, ('snippet', 'totalReplyCount')),
                        'commentDate': get_data_or_none(c, ('snippet', 'topLevelComment', 'snippet', 'updatedAt'))
                    }
                    tmp_comments.append(comment_data)

                next_page_token = comment_response.get('nextPageToken')

                if not next_page_token:
                    break
            
            # コメントが無効になっている場合にエラーをはかないようにするため
            except HttpError as e:
                error = json.loads(e.content)
                if error['error']['errors'][0]['reason'] == 'commentsDisabled':
                    # コメントが無効になっている場合はスキップして次の動画に進む
                    break
                    
                elif error['error']['errors'][0]['reason'] == 'quotaExceeded':
                    # これ以降のすべてのvideoIdをerror_idsに追加
                    print(f"An error occurred: {error}\nvideo_id：{video_id}　{i}")
                    error_ids.extend([(vid, 'quotaExceeded') for vid in video_ids[i-1:]])
                    exit_outer_loop = True
                    break
                    
                else:
                    # その他のエラーは処理を停止せず、エラーメッセージを表示して続行
                    print(f"An error occurred: {error}\nvideo_id：{video_id}　{i}")
                    error_ids.append([video_id, error['error']['errors'][0]['reason']])
                    break
        
        if exit_outer_loop:
            break      
        else:
            comments.extend(tmp_comments)
            
        if (i+1)%50 == 0 or i==n-1:
            # 50回ごとの時間の計測
            end_time = time.time()
            lap_time = end_time - start_time
            elapsed_time = end_time - start0_time
            
            print(f"{i+1}/{n}個目完了　コメント数：{len(comments)-n_tmp}　時間：{lap_time:.3f}　　総経過時間：{elapsed_time:.0f}")
            n_tmp = len(comments)
            start_time = time.time()
            


    if save:            
        destination_folder = f'data/{channel}'
        os.makedirs(destination_folder, exist_ok=True)  # 移動先フォルダが存在しない場合は作成する
        # 結果をJSONファイルで保存
        df_comments = pd.DataFrame(comments)
        df_comments.to_json(f'{destination_folder}/{channel}_comments{k}.json', orient='records', date_format='iso')
        
        # エラーでとれなかった動画idを保存
        df_errors = pd.DataFrame(error_ids)
        df_errors.to_json(f'{destination_folder}/{channel}_errorIds.json', orient='records')
        
    print(f"総コメント数：{len(comments)}\n保存完了\n{channel}_comments{k}.json")
    # winsound.Beep(440, 1500)  # 440Hzの音を1.5秒間再生
    
    return comments, error_ids

                
def remove_duplicates(df, column):
    # 重複する要素を検索
    duplicates = df[column][df[column].duplicated()]
    
    if len(duplicates) > 0:
        # 重複要素をプリント
        print("重複する要素:")
        print(duplicates)
        
        # ユーザーの確認を取る
        answer = input("重複を削除しますか？(y/n): ")
        if answer.lower() == 'y':
            # 重複を削除
            df = df.drop_duplicates(subset=column)
            print("重複が削除されました。")
        else:
            print("重複削除はキャンセルされました。")
            
    else:
        print("重複はありません")
        
    return df

# 各コメントの言語判定
def lang_dist(comments_txt):
    lang_counts = Counter()
    for comment in comments_txt:
        try:
            lang_info = detect_langs(comment)
            for info in lang_info:
                lang = info.lang
                prob = info.prob
                lang_counts[lang] += prob
        except LangDetectException:
            # エラーが発生した場合は無視して処理を続行
            pass

    # 各言語のコメント数と割合の計算
    total_comments = sum(lang_counts.values())
    lang_percentages = {lang: count / total_comments for lang, count in lang_counts.items()}
    
    return lang_percentages

def get_statistics(comments_txt, channel=None):
    # コメントの文字数を取得
    comment_lengths = [len(comment) for comment in comments_txt]

    # ヒストグラムの表示
    plt.hist(comment_lengths, bins=20, log=True)
    # plt.xscale('log')
    plt.xlabel("コメントの文字数", fontproperties=font_prop)
    plt.ylabel("出現回数", fontproperties=font_prop)
    plt.title("コメントの文字数の分布", fontproperties=font_prop)
    plt.savefig(f"data/{channel}/{channel}_hist.png")  # ヒストグラムを保存
    plt.show()

    # 統計的な指標の計算
    mean_length = np.mean(comment_lengths)  # 平均
    median_length = np.median(comment_lengths)  # 中央値
    min_length = np.min(comment_lengths)  # 最小値
    max_length = np.max(comment_lengths)  # 最大値
    std_length = np.std(comment_lengths)  # 標準偏差
    max_comment = max(comments_txt, key=len) # 最長のコメント

    print("コメントの数：", len(comments_txt))
    print("平均文字数：", mean_length)
    print("中央値文字数：", median_length)
    print("最小文字数：", min_length)
    print("最大文字数：", max_length)
    print("標準偏差：", std_length)
    print("最長のコメント：", max_comment[:1000])
    
    statistics = {
        "num_comments":str(len(comments_txt)),
        "mean_length": str(mean_length),
        "median_length": str(median_length),
        "min_length": str(min_length),
        "max_length": str(max_length),
        "std_length": str(std_length),
        "max_comment": max_comment
    }
    if channel:
        # 統計情報を保存
        with open(f"data/{channel}/{channel}_statistics.json", "w", encoding="utf-8") as f:
            json.dump(statistics, f, ensure_ascii=False, indent=4)
            
    return statistics