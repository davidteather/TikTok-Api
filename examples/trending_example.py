from TikTokApi import TikTokApi

verify_fp = "verify_xxx"
with TikTokApi(custom_verify_fp=verify_fp) as api:
    for video in api.trending.videos():
        print(video.id)
