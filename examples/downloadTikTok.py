from TikTokApi import TikTokApi
import random

# SEE https://github.com/davidteather/TikTok-Api/issues/311#issuecomment-721164493

# Starts TikTokApi
api = TikTokApi.get_instance()

# This is generating the tt_webid_v2 cookie
# need to pass it to methods you want to download
did = str(random.randint(10000, 999999999))

trending = api.trending(custom_did=did)

# Below is if the method used if you have the full tiktok object
tiktokData = api.get_Video_By_TikTok(trending[0], custom_did=did)

with open("video.mp4", "wb") as out:
    out.write(tiktokData)
