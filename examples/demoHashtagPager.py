from datetime import datetime
from TikTokApi import TikTokApi

api = TikTokApi(debug=True)


def printPage(page):
    """Just prints out each post with timestamp and description"""
    for p in page:
        post = p['itemInfos']
        print("{}: {}".format(datetime.fromtimestamp(int(post['createTime'])), post['text']))


count = 50
hashtag = 'funny'

pager = api.getHashtagPager(hashtag, page_size=count)

total = 0
oldest = None
for posts in pager:
    for post in posts:
        created_at = int(post['itemInfos']['createTime'])

        if oldest is None:
            oldest = created_at

        if created_at < oldest:
            oldest = created_at

    # printPage(posts)
    total += len(posts)

if oldest is None:
    print('Nothing found')
else:
    print(f"found {total} posts for #{hashtag}. Oldest is from {datetime.fromtimestamp(oldest)}")
