from TikTokApi import TikTokapi

# Starts T
api = TikTokapi("path/to/browsermob-proxy")

# The Number of TikToks you want to be displayed
results = 10
soundTikToks = api.search_by_sound("https://www.tiktok.com/music/original-sound-6742171751955843846")

for tiktok in soundTikToks:
    # Prints the text of the tiktok
    print(tiktok['itemInfos']['text'])

print(len(soundTikToks))
api.quit_browser()
