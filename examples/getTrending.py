from TikTokApi import TikTokapi

# Starts T
api = TikTokapi("path/to/browsermob-proxy")

# The Number of trending TikToks you want to be displayed
results = 10
trending = api.trending(results)

for tiktok in trending:
    # Prints the text of the tiktok
    print(tiktok['itemInfos']['text'])

print(len(trending))

api.quit_browser()