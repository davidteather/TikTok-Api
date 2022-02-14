from TikTokApi import TikTokApi

verify_fp = "verify_xxx"
api = TikTokApi(custom_verify_fp=verify_fp)

user = api.user(username="therock")

for video in user.videos():
    print(video.id)

for liked_video in api.user(username="public_likes").videos():
    print(liked_video.id)
