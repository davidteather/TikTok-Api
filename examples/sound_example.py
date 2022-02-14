from TikTokApi import TikTokApi

verify_fp = "verify_xxx"
api = TikTokApi(custom_verify_fp=verify_fp)

sound = api.sound(id="7016547803243022337")

for video in sound.videos():
    print(video.id)
