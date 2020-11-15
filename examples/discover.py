from TikTokApi import TikTokApi

api = TikTokApi()

# Gets array of trending music objects
trendingMusic = api.discoverMusic()

for tiktok in trendingMusic:
    print(tiktok)

# Gets array of trending challenges (hashtags)
trendingChallenges = api.discoverHashtags()

for tiktok in trendingChallenges:
    print(tiktok)
