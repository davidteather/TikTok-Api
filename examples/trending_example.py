from TikTokApi import TikTokApi

verify_fp = "verify_xxx"
api = TikTokApi(custom_verify_fp=verify_fp)

for video in api.trending.videos():
    print(video.id)
