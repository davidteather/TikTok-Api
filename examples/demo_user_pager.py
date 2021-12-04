from datetime import datetime
from TikTokApi import TikTokApi

api = TikTokApi(debug=True)


def printPage(page):
    """Just prints out each post with timestamp and description"""
    for post in page:
        print("{}: {}".format(datetime.fromtimestamp(post["createTime"]), post["desc"]))


count = 20
username = "therock"

# count and list all of the posts for a given user with the pager
total = 0

pager = api.get_user_pager(username, page_size=count)

for page in pager:
    printPage(page)
    total += len(page)

print("{} has {} posts".format(username, total))
all_posts = total

# List all of the posts for a given user after a certain date

APR_24 = 1587757438000  # 2020-04-24 15:43:58 to be precise. Must be ms-precision UNIX timestamp
user = api.get_user_object(username)
page = api.user_page(user["id"], user["secUid"], page_size=30, after=APR_24)

printPage(page["itemList"])
new_posts = len(page["itemList"])
print("{} has {} posts after {}".format(username, new_posts, APR_24))


# Count and list all of the posts before a certain date for a given user with the pager

total = 0
pager = api.get_user_pager(username, page_size=count, before=APR_24)

for page in pager:
    printPage(page)
    total += len(page)

print("{} has {} posts from before {}".format(username, total, APR_24))
print("Should be {}".format(all_posts - new_posts))
