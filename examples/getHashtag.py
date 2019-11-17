from TikTokApi import TikTokapi

# Starts The Api Class
api = TikTokapi("browsermob-proxy/bin/browsermob-proxy")

# The Number of trending TikToks you want to be displayed
results = 10

result = api.search_by_hashtag("funny")

for tiktok in result:
    print(tiktok)

print(len(result))

api.quit_browser()