# NOTE: This python file cannot be run from the examples folder.
# It MUST BE in the same directory as tiktok.py is located!
# Yeah sorry, it's kind of annoying, but it's more organized this way.
from TikTokApi import TikTokapi

# Starts T
api = TikTokapi("browsermob-proxy/bin/browsermob-proxy")

# The Number of trending TikToks you want to be displayed
results = 10
trending = api.trending(results)

for tiktok in trending:
    # Prints the music play URL for the tiktok in trending
    print(tiktok['musicInfos']['playUrl'][0])

    # Prints the text of the tiktok
    print(tiktok['itemInfos']['text'])

print(len(trending))