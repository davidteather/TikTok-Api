from TikTokApi import TikTokapi

def getUser(results):
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=True)
    result = api.userPosts("5058536", "MS4wLjABAAAAoRsCq3Yj6BtSKBCQ4rf3WQYxIaxe5VetwJfYzW_U5K8", count=results)
    api.quit_browser()

    return len(result)


def test_trending():
    assert getUser(5) == 5
    assert getUser(10) == 10
    assert getUser(30) == 30