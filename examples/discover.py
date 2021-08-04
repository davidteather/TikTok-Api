from TikTokApi import TikTokApi

api = TikTokApi.get_instance()

# Gets array of trending music objects
trendingMusic = api.discover_music()

for tiktok in trendingMusic:
    print(tiktok)

# Gets array of trending challenges (hashtags)
trendingChallenges = api.discover_hashtags()

for tiktok in trendingChallenges:
    print(tiktok)
