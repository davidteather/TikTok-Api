from TikTokApi import TikTokapi

def getUser(results):
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=False)
    result = api.userPosts("jadenthekingsley", count=results)
    api.quit_browser()

    return len(result)


def test_trending():
    assert getUser(5) == 5
    assert getUser(10) == 10