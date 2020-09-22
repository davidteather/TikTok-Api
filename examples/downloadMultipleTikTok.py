import os
import glob
import cv2
from TikTokApi import TikTokApi


def clearTMP(delpath):
    r = glob.glob(delpath)
    for i in r:
        os.remove(i)

if not os.path.exists("downloaded"):
    os.mkdir('downloaded')

if not os.path.exists("output"):
    os.mkdir("output")

clearTMP('output/output.mp4')

# Vars
count = 30
api = TikTokApi()

tiktokData = api.trending(count=count)
tiktokData = api.byHashtag('funny', count=count)
tiktokData = api.bySound('6601861313180207878', count=count)
# tiktokData = api.byUsername('americanredcross', count=count)
prevloops = 0
for res in tiktokData:
    open('downloaded/' + str(prevloops) +
            ".mp4", "wb").write(api.get_Video_By_TikTok(res))