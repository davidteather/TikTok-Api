from TikTokApi import TikTokapi

# Starts The Api Class
api = TikTokapi("browsermob-proxy/bin/browsermob-proxy")

# The Number of trending TikToks you want to be displayed
results = 10

# The TikTok user's ID, can be found in the JSON from trending
id = "7119601"

trending = api.userPosts(id, count=results)

for tiktok in trending:
    # Prints the text of the tiktok
    print(tiktok['itemInfos']['text'])

print(len(trending))