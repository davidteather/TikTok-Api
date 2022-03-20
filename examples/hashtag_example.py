from TikTokApi import TikTokApi

with TikTokApi() as api:
    tag = api.hashtag(name="funny")

    print(tag.info())

    for video in tag.videos():
        print(video.id)
