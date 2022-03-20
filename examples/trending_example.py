from TikTokApi import TikTokApi

with TikTokApi() as api:
    for video in api.trending.videos():
        print(video.id)
