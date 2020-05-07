from TikTokApi import TikTokApi
# Starts TikTokApi
api = TikTokApi()

tiktokData = api.get_Video_By_Url("https://www.tiktok.com/@ceciliaannborne/video/6817602864228207878", return_bytes=1)

with open("video.mp4", 'wb') as out:
    out.write(tiktokData)