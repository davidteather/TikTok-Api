from TikTokApi import TikTokApi

api = TikTokApi()

# If you want to get a variety of users from suggested users you need to provide various
# userIds to the getSuggestedUsersbyID function. So here's an example to do that.

usersToCrawl = 50

userId = "6745191554350760966"  # This is therock's userId for TikTok you can change it to whereever you want to start crawling from

api.getSuggestedUsersbyIDCrawler(startingId=userId)
