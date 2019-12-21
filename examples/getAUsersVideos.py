from TikTokApi import TikTokapi

# Starts The Api Class
api = TikTokapi("browsermob-proxy/bin/browsermob-proxy")

# The Number of trending TikToks you want to be displayed
results = 10

# The TikTok user's ID, can be found in the JSON from trending
id = "6667259165620912134"

# The TikTok user's secUid, can be found in the Json from trending
secUid = "MS4wLjABAAAAmROcF0HiS0_I562i4obaZJDpFVZ5IegSTj_Z3zE-Mf_BDx0OoiibJ3TMeYeCLrhx"

trending = api.userPosts(id, secUid, count=results)

for tiktok in trending:
    # Prints the text of the tiktok
    print(tiktok['itemInfos']['text'])

print(len(trending))
api.quit_browser()
