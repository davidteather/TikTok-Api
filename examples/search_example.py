from TikTokApi import TikTokApi

verify_fp = "verify_xxx"

with TikTokApi(custom_verify_fp=verify_fp) as api:
    for user in api.search.users("therock"):
        print(user.username)

    for sound in api.search.sounds("funny"):
        print(sound.title)

    for hashtag in api.search.hashtags("funny"):
        print(hashtag.name)
