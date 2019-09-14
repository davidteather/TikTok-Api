from TikTokApi import TikTokapi

def getUser(results):
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=True)
    result = api.userPosts("6718751032510759942", count=results)

    return len(result)


def test_trending():
    assert getUser(10) == 10
    assert getUser(20) == 20
    assert getUser(30) == 30