from TikTokApi import TikTokApi

api = TikTokApi(debug=True)

def printPage(page):
    """Just prints out each post with timestamp and description"""
    for post in page:
        print("{}: {}".format(post['createTime'], post['desc']))

count = 20
username = 'diply'

# count and list all of the posts for a given user with the pager
total = 0

pager = api.getUserPager(username, page_size=count)

for page in pager:
    printPage(page)
    total += len(page)

print('{} has {} posts'.format(username, total))
all_posts = total

# List all of the posts for a given user after a certain date
AUG_19 = 1597889080000  # 2020-8-19 22:04:40 to be precise. Must be ms-precision UNIX timestamp
user = api.getUserObject(username)
page = api.userPage(user['id'], user['secUid'], page_size=30, after=AUG_19)

printPage(page['items'])
new_posts = len(page['items'])
print('{} has {} posts after {}'.format(username, new_posts, AUG_19))


# Count and list all of the posts before a certain date for a given user with the pager

total = 0
pager = api.getUserPager(username, page_size=count, before=AUG_19)

for page in pager:
    printPage(page)
    total += len(page)

print('{} has {} posts from before {}'.format(username, total, AUG_19))
print('Should be {}'.format(all_posts - new_posts))
