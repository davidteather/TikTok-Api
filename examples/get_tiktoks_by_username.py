from TikTokApi import TikTokApi

api = TikTokApi.get_instance()

count = 30

tiktoks = api.by_username("americanredcross", count=count)

for tiktok in tiktoks:
    print(tiktok)
