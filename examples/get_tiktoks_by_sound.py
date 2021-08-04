from TikTokApi import TikTokApi

api = TikTokApi.get_instance()

count = 30

# You can find this from a tiktok getting method in another way or find songs from the discoverMusic method.
sound_id = "6601861313180207878"

tiktoks = api.by_sound(sound_id, count=count)

for tiktok in tiktoks:
    print(tiktok)
