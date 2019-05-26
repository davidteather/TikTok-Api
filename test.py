from tiktok import TikTokapi

api = TikTokapi()

print(api.userPosts(6614616633741737990, 10)[0])