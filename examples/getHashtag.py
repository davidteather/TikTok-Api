from TikTokApi import TikTokapi

# Starts The Api Class
api = TikTokapi("browsermob-proxy/bin/browsermob-proxy")

# The Number of trending TikToks you want to be displayed
results = 10

# Gets trending hashtags
trending_tags = api.get_trending_hashtags()

# Searches for the top trending hashtag of TikTok
result = api.search_by_hashtag(trending_tags[0])

for tiktok in result:
    # Prints the text of the tiktok
    print(tiktok['itemInfos']['text'])

print(len(result))

api.quit_browser()