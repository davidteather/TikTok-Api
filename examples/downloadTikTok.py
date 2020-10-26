from TikTokApi import TikTokApi

# Starts TikTokApi
api = TikTokApi()

# Below is used if you have the download url from the tiktok object, but maybe not the full object
tiktokData = api.get_Video_By_DownloadURL(
    api.trending(count=1)[0]["video"]["downloadAddr"]
)

# Below is if the method used if you have the full tiktok object
tiktokData = api.get_Video_By_TikTok(api.trending(count=1)[0])

# Below is used if you want no watermarks
tiktokData = api.get_Video_No_Watermark(
    "https://www.tiktok.com/@ceciliaannborne/video/6817602864228207878", return_bytes=1
)

with open("video.mp4", "wb") as out:
    out.write(tiktokData)
