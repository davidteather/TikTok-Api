from TikTokApi import TikTokApi

verify_fp = "verify_xxx"
api = TikTokApi(custom_verify_fp=verify_fp)

tag = api.hashtag(name="funny")

print(tag.info())

for video in tag.videos():
    print(video.id)
