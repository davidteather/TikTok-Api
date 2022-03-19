from TikTokApi import TikTokApi

verify_fp = "verify_xxx"
with TikTokApi(custom_verify_fp=verify_fp) as api:
    tag = api.hashtag(name="funny")

    print(tag.info())

    for video in tag.videos():
        print(video.id)
