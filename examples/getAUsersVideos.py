from TikTokApi import TikTokapi

# Starts The Api Class
api = TikTokapi("browsermob-proxy/bin/browsermob-proxy")

# The Number of trending TikToks you want to be displayed
results = 10

userPosts = api.userPosts("khaleelabdullah_")

for tiktok in userPosts:
    print(tiktok)

print(len(trending))

api.quit_browser()