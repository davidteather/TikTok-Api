from TikTokApi import TikTokApi

verify_fp = "verify_xxx"
with TikTokApi(custom_verify_fp=verify_fp) as api:
    user = api.user(username="therock")

    for video in user.videos():
        print(video.id)

    for liked_video in api.user(username="public_likes").videos():
        print(liked_video.id)
