from TikTokApi import TikTokApi

api = TikTokApi()

count = 30

# You can find this from a tiktok getting method in another way or find songs from the discoverMusic method.
soundId = '6601861313180207878'

tiktoks = api.bySound(soundId, count=count)

for tiktok in tiktoks:
    print(tiktok)