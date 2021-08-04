from TikTokApi import TikTokApi

# Starts TikTokApi
api = TikTokApi.get_instance()

# The Number of trending TikToks you want to be displayed
results = 10

# Returns a list of dictionaries of the trending object
userPosts = api.user_posts(
    "6745191554350760966",
    "MS4wLjABAAAAM3R2BtjzVT-uAtstkl2iugMzC6AtnpkojJbjiOdDDrdsTiTR75-8lyWJCY5VvDrZ",
    30,
)
# Loops over every tiktok
for tiktok in userPosts:
    # Prints the text of the tiktok
    print(tiktok["desc"])

print(len(userPosts))
