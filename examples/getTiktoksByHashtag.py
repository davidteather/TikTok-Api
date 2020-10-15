from TikTokApi import TikTokApi

api = TikTokApi()

count = 30

tiktoks = api.byHashtag("funny", count=count)

for tiktok in tiktoks:
    print(tiktok)
